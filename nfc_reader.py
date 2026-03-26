from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.Exceptions import NoCardException, CardConnectionException

class NFCReader:
    def __init__(self):
        """Inicializa el lector NFC"""
        self.reader = None
        self.connection = None
    
    def detectar_lector(self):
        """Detecta si hay un lector NFC conectado"""
        try:
            r = readers()
            if len(r) == 0:
                return False, "No se detectó ningún lector NFC"
            
            self.reader = r[0]
            return True, f"Lector detectado: {self.reader}"
        
        except Exception as e:
            return False, f"Error al detectar lector: {str(e)}"
    
    def leer_tarjeta(self):
        """Lee el UID de la tarjeta NFC"""
        try:
            self.connection = self.reader.createConnection()
            self.connection.connect()
            
            GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            data, sw1, sw2 = self.connection.transmit(GET_UID)
            
            if sw1 == 0x90 and sw2 == 0x00:
                uid = toHexString(data).replace(" ", "")
                return True, uid
            else:
                return False, f"Error en la lectura: SW1={hex(sw1)}, SW2={hex(sw2)}"
        
        except NoCardException:
            return False, "No hay tarjeta en el lector"
        
        except CardConnectionException:
            return False, "Error de conexión con el lector"
        
        except Exception as e:
            return False, f"Error: {str(e)}"
        
        finally:
            if self.connection:
                try:
                    self.connection.disconnect()
                except:
                    pass