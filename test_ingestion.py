from core.ingestion.vehicle_mapper import VehicleMapper
import os

def test_ingestion():
    mapper = VehicleMapper()
    
    # 1. Test CSV Loading
    print("--- Testing CSV Loading ---")
    base_path = r"G:\My Drive\snapshot_data"
    dtc_path = os.path.join(base_path, "ISO14229DTCs_DTC_CODES.csv")
    
    if os.path.exists(dtc_path):
        mapper.load_iso_definitions(dtc_path=dtc_path)
        print(f"Loaded {len(mapper.iso_dtcs)} DTCs.")
        print(f"Sample: B0001 -> {mapper.iso_dtcs.get('B0001')}")
    else:
        print("CSV file not found, skipping.")

    # 2. Test JLR CFG Parsing
    print("\n--- Testing JLR CFG Parsing ---")
    cfg_path = os.path.join(base_path, "SS5_EMA_L384_28MY.cfg")
    
    if os.path.exists(cfg_path):
        success = mapper.import_jlr_config(cfg_path)
        if success:
            veh = mapper.current_vehicle
            print(f"Vehicle: {veh.name}")
            print(f"ECU Count: {len(veh.ecus)}")
            
            # Detail Check: BCMA
            bcma_addr = 0x726
            if bcma_addr in veh.ecus:
                node = veh.ecus[bcma_addr]
                print(f"Found Node: {node['name']} ({node['description']})")
                print(f"DID Count: {len(node['dids'])}")
                
                # Check specific DID 0xE103
                target_did = 0xE103
                if target_did in node['dids']:
                    did = node['dids'][target_did]
                    print(f"  DID 0x{target_did:X}: {did['name']} (Cmd: {did['read_cmd']})")
                else:
                    print(f"  DID 0xE103 not found!")
            else:
                print("BCMA (0x726) not found!")
        else:
            print("Failed to parse CFG.")
    else:
        print("CFG file not found.")

if __name__ == "__main__":
    test_ingestion()
