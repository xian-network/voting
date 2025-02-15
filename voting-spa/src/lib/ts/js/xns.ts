import { get } from "svelte/store"
import { requestXnsLookup } from "./api/api"
import { xnsLookupsStore } from "./store"

export const updateXnsLookups = async (addresses: string[]) => {
    const currentLookups = get(xnsLookupsStore)
    const toLookup = addresses.filter(address => !currentLookups[address])

    if (toLookup.length === 0) return

    const res = await requestXnsLookup(toLookup)
    for (const address of addresses) {
        currentLookups[address] = JSON.parse(res.result.replace(/'/g, '"'))[address]
    }
    xnsLookupsStore.set(currentLookups)
    return currentLookups
}