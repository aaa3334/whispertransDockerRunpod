import os
import shutil
import runpod
from runpod.serverless.utils.rp_validator import validate
from runpod.serverless.utils import download_files_from_urls, rp_cleanup
from rp_schema import INPUT_VALIDATIONS
from crisper_predictor import CrisperPredictor, Output

MODEL = CrisperPredictor()
MODEL.setup()

def cleanup_job_files(job_id, jobs_directory='/jobs'):
    job_path = os.path.join(jobs_directory, job_id)
    if os.path.exists(job_path):
        try:
            shutil.rmtree(job_path)
            print(f"Removed job directory: {job_path}")
        except Exception as e:
            print(f"Error removing job directory {job_path}: {str(e)}")
    else:
        print(f"Job directory not found: {job_path}")

def run(job):
    job_input = job['input']
    job_id = job['id']
    
    # Input validation
    validated_input = validate(job_input, INPUT_VALIDATIONS)
    if 'errors' in validated_input:
        return {"error": validated_input['errors']}
    
    if 'audio_file' not in job_input and 'audio_base64' not in job_input:
        return {"error": "Either audio_file URL or audio_base64 must be provided"}

    # Handle base64 input
    if 'audio_base64' in job_input:
        import base64
        import tempfile
        
        # Decode base64 and save to temporary file
        audio_data = base64.b64decode(job_input['audio_base64'])
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_file.write(audio_data)
            audio_file_path = temp_file.name
    else:
        # Original URL handling
        audio_file_path = download_files_from_urls(job['id'], [job_input['audio_file']])[0]

    # Prepare input for prediction
    predict_input = {
        'audio_file': audio_file_path,
        'language': job_input.get('language'),
        'batch_size': job_input.get('batch_size', 16),
        'temperature': job_input.get('temperature', 0),
        'debug': job_input.get('debug', False)
    }
    
    # Run prediction
    try:
        result = MODEL.predict(**predict_input)
        
        # Simplify output to just return transcription and language
        output_dict = {
            "transcription": result.transcription,
            "detected_language": result.detected_language
        }
        
        # Cleanup downloaded files
        rp_cleanup.clean(['input_objects'])
        cleanup_job_files(job_id)
        
        return output_dict
    except Exception as e:
        return {"error": str(e)}

runpod.serverless.start({"handler": run})
