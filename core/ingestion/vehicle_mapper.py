class VehicleArchitecture:
    """
    Represents the learned architecture of a vehicle.
    """
    def __init__(self, name="Unknown Vehicle"):
        self.name = name
        self.ecus = {} # {address_int: ECU}
        self.dtc_map = {} # {code_str: description}
        self.did_map = {} # {did_hex_str: description}

    def add_ecu(self, name, address, description="", network=""):
        if address not in self.ecus:
            self.ecus[address] = {
                'name': name,
                'address': address,
                'description': description,
                'network': network,
                'dids': {} # {did_id_int: {'name': str, 'len': int, 'read_cmd': list}}
            }
        return self.ecus[address]

    def add_did_to_ecu(self, ecu_addr, did_id, name, read_cmd_bytes, tag=""):
        if ecu_addr in self.ecus:
            self.ecus[ecu_addr]['dids'][did_id] = {
                'name': name,
                'read_cmd': read_cmd_bytes,
                'tag': tag
            }

class VehicleMapper:
    """
    Manager for ingestion and architecture storage.
    """
    def __init__(self):
        self.current_vehicle = VehicleArchitecture()
        self.iso_dtcs = {} # Global lookup
        self.iso_nrcs = {}
        self.iso_faults = {}
        
        # Auto-load ISO resources if available
        self._auto_load_resources()

    def _auto_load_resources(self):
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) # core/ingestion/.. -> core/.. -> root
        iso_dir = os.path.join(base_dir, 'resources', 'iso')
        
        if os.path.exists(iso_dir):
            self.load_iso_definitions(
                dtc_path=os.path.join(iso_dir, 'ISO14229DTCs_DTC_CODES.csv'),
                nrc_path=os.path.join(iso_dir, 'ISO14229NRCs_NRC_CODES.csv'),
                fault_path=os.path.join(iso_dir, 'ISO14229DTCs_FAULT_TYPES.csv')
            )
    def load_iso_definitions(self, dtc_path=None, nrc_path=None, fault_path=None):
        from .parsers.csv_loader import CSVLoader
        loader = CSVLoader()
        if dtc_path:
            self.iso_dtcs.update(loader.load_dtcs(dtc_path))
        if nrc_path:
            self.iso_nrcs.update(loader.load_nrcs(nrc_path))
        if fault_path:
            self.iso_faults.update(loader.load_fault_types(fault_path))

    def import_jlr_config(self, cfg_path):
        from .parsers.jlr_cfg_parser import JLRConfigParser
        parser = JLRConfigParser()
        new_arch = parser.parse(cfg_path)
        if new_arch:
            self.current_vehicle = new_arch
            return True
        return False
