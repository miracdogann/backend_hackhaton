import base64

def array_buffer_to_base64(buffer):
    """
    Bayt dizisini base64 kodlu bir dizeye dönüştürür.
    
    Args:
        buffer (bytes): Kodlanacak bayt dizisi (örneğin, görüntü verisi).
    
    Returns:
        str: Giriş buffer'ının base64 kodlu dizesi.
    """
    return base64.b64encode(buffer).decode('utf-8')