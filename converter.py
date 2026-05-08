import struct

class converters:

    @staticmethod
    def StringToBytes(text):
        return text.encode('utf-8')
    
    @staticmethod
    def BytesToString(bytes_data):
        return bytes_data.decode('utf-8')
    
    @staticmethod
    def IntToBytes(value):
         return struct.pack('i', value)
    
    @staticmethod
    def BytesToInt(bytes_data):
        return struct.unpack('i', bytes_data)[0]