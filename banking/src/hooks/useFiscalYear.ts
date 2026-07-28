import { useFrappeGetCall } from "frappe-react-sdk"

const useFiscalYear = () => {

    return useFrappeGetCall("mes_euidos.accounts.utils.get_fiscal_year", undefined, 'fiscal_year', {
        revalidateOnFocus: false,
        revalidateIfStale: false,
        revalidateOnReconnect: false
    })

}

export default useFiscalYear