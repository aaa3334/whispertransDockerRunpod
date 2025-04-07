INPUT_VALIDATIONS = {
    'audio_file': {
        'type': str,
        'required': True
    },
    
    'language': {
        'type': str,
        'required': False,
        'default': None
    },
    'batch_size': {
        'type': int,
        'required': False,
        'default': 16
    },
    'temperature': {
        'type': float,
        'required': False,
        'default': 0
    },
    'debug': {
        'type': bool,
        'required': False,
        'default': False
    }
}