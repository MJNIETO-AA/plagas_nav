from src.reports.services_report import export_services_excel, export_services_pdf


def main():
    xlsx_path = export_services_excel()
    pdf_path = export_services_pdf()

    print("Excel generado en:", xlsx_path)
    print("PDF generado en:", pdf_path)


if __name__ == "__main__":
    main()