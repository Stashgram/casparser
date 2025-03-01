import io
from typing import Union

from casparser.transform import process_cas_text
from casparser.commontypes import FolioType
from casparser.extract.utils import cas2json, cas2csv

print("hey")


def read_cas_pdf(
        filename: Union[str, io.IOBase],
        password,
        output="dict",
        sort_transactions=False,
        force_pdfminer=False,
):
    """
    Parse CAS pdf and returns line data.

    :param filename: CAS pdf file (CAMS or Kfintech)
    :param password: CAS pdf password
    :param output: Output format (json,dict)  [default: dict]
    :param sort_transactions: Sort transactions by date and re-compute balances.
    :param force_pdfminer: Force pdfminer parser even if mupdf is detected
    """
    print("hey")
    if force_pdfminer:
        from casparser.extract.pdfminerhelper import cas_pdf_to_text
    else:
        try:
            from casparser.extract.mupdfhelper import cas_pdf_to_text
        except (ImportError, ModuleNotFoundError):
            from casparser.extract.pdfminerhelper import cas_pdf_to_text

    partial_cas_data = cas_pdf_to_text(filename, password)
    print(partial_cas_data)
    processed_data = process_cas_text("\u2029".join(partial_cas_data.lines))

    if sort_transactions:
        folio: FolioType
        for folio in processed_data.get("folios"):
            for scheme in folio["schemes"]:
                dates = [x["date"] for x in scheme["transactions"]]
                sorted_dates = list(sorted(dates))
                if dates != sorted_dates:
                    sorted_transactions = []
                    balance = scheme["open"]
                    for transaction in sorted(scheme["transactions"], key=lambda x: x["date"]):
                        balance += transaction["units"] or 0
                        transaction["balance"] = balance
                        sorted_transactions.append(transaction)
                    scheme["transactions"] = sorted_transactions

    # noinspection PyProtectedMember
    processed_data.update(
        {
            "file_type": partial_cas_data.file_type.name,
            "investor_info": partial_cas_data.investor_info._asdict(),
        }
    )
    if output == "dict":
        return processed_data
    elif output == "csv":
        return cas2csv(processed_data)
    return cas2json(processed_data)


read_cas_pdf("E:\Stashgam\casparser\cams.pdf", "FOXPS4837B")
