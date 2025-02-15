import con_name_service_final

@export
def multicall(addresses: list):
    results = {}
    for address in addresses:
        res = con_name_service_final.get_address_to_main_name(address)
        results[address] = res if res else ""
    return results
