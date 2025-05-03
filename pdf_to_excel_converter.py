import streamlit as st
import pandas as pd
import pdfplumber
import io

def extract_data_from_pdf(pdf_file):
    data = []
    date_range = income = expense = balance = ""
    
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
                
            lines = text.split('\n')
            
            # Extract header information
            for i, line in enumerate(lines):
                if "Laporan Keuangan" in line:
                    try:
                        date_range = lines[i+1].split(":")[1].strip() if i+1 < len(lines) else ""
                        income = lines[i+2].split(":")[1].strip() if i+2 < len(lines) else ""
                        expense = lines[i+3].split(":")[1].strip() if i+3 < len(lines) else ""
                        balance = lines[i+4].split(":")[1].strip() if i+4 < len(lines) else ""
                    except IndexError:
                        pass
                    break
            
            # Process table data
            for line in lines:
                if not line.strip() or line.startswith("File ini dibuat oleh"):
                    continue
                    
                parts = line.split()
                if len(parts) < 5:
                    continue
                    
                try:
                    no = parts[0]
                    date = ' '.join(parts[1:3]) if len(parts) >= 3 else ""
                    
                    # Find the split between description and amounts
                    amount_start = -1
                    for i, part in enumerate(parts):
                        if part.startswith('Rp'):
                            amount_start = i
                            break
                    
                    if amount_start == -1:
                        continue
                        
                    description = ' '.join(parts[3:amount_start])
                    
                    # Get amounts and category
                    amounts = parts[amount_start:]
                    expense_amount = amounts[0] if len(amounts) > 0 and amounts[0].startswith('Rp') else ""
                    income_amount = amounts[1] if len(amounts) > 1 and amounts[1].startswith('Rp') else ""
                    
                    # Find category (last word if it's a known category)
                    categories = ['Makanan', 'Belanja', 'Lain-lain', 'Deposito', 'Pakaian', 'Pengembalian']
                    category = parts[-1] if parts[-1] in categories else ""
                    
                    data.append({
                        'No': no,
                        'Tanggal': date,
                        'Keterangan': description,
                        'Pengeluaran': expense_amount,
                        'Pemasukan': income_amount,
                        'Kategori': category
                    })
                except Exception as e:
                    st.warning(f"Gagal memproses baris: {line}. Error: {str(e)}")
                    continue
    
    return date_range, income, expense, balance, data

def create_excel_template(date_range, income, expense, balance, transactions):
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Create summary sheet
        summary_data = [
            ["LAPORAN KEUANGAN", "", "", "", ""],
            ["Tanggal", date_range, "", "", ""],
            ["Pemasukan", income, "", "", ""],
            ["Pengeluaran", expense, "", "", ""],
            ["Saldo", balance, "", "", ""]
        ]
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Ringkasan', index=False, header=False)
        
        # Format summary sheet
        workbook = writer.book
        worksheet = writer.sheets['Ringkasan']
        
        # Format header
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        worksheet.merge_range('A1:E1', 'LAPORAN KEUANGAN', header_format)
        
        # Create transactions sheet
        transactions_df = pd.DataFrame(transactions)
        transactions_df.to_excel(writer, sheet_name='Transaksi', index=False)
        
        # Format transactions sheet
        worksheet = writer.sheets['Transaksi']
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        for col_num, value in enumerate(transactions_df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Adjust column widths
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 12)
        worksheet.set_column('C:C', 40)
        worksheet.set_column('D:D', 12)
        worksheet.set_column('E:E', 12)
        worksheet.set_column('F:F', 15)
    
    output.seek(0)
    return output

def main():
    st.title('Konversi Laporan Keuangan PDF ke Excel')
    st.write('Unggah laporan keuangan dalam format PDF untuk dikonversi ke Excel')
    
    uploaded_file = st.file_uploader("Pilih file PDF", type="pdf")
    
    if uploaded_file is not None:
        try:
            date_range, income, expense, balance, transactions = extract_data_from_pdf(uploaded_file)
            
            st.success("Data berhasil diekstrak dari PDF!")
            
            st.subheader("Ringkasan Laporan Keuangan")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Periode", date_range)
            with col2:
                st.metric("Total Pemasukan", income)
            with col3:
                st.metric("Total Pengeluaran", expense)
            
            st.metric("Saldo Akhir", balance)
            
            st.subheader("Preview Data Transaksi (10 baris pertama)")
            st.dataframe(pd.DataFrame(transactions).head(10))
            
            excel_file = create_excel_template(date_range, income, expense, balance, transactions)
            
            st.download_button(
                label="Unduh File Excel",
                data=excel_file,
                file_name=f"Laporan_Keuangan_{date_range.replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Klik untuk mengunduh file Excel"
            )
            
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses file: {str(e)}")
            st.error("Pastikan format PDF sesuai dengan contoh. Jika masalah berlanjut, coba periksa struktur file PDF Anda.")

if __name__ == "__main__":
    main()