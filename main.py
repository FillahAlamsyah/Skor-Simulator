import streamlit as st
import pandas as pd
import html
import uuid
import io, requests, urllib.request
from fpdf import FPDF
from pdf2image import convert_from_bytes
from streamlit_pdf_viewer import pdf_viewer
st.set_page_config(page_title='Skor Simulator', page_icon=':soccer:', layout='centered', initial_sidebar_state='expanded')

def inject_js_code(source: str) -> None:
    div_id = uuid.uuid4()

    st.markdown(
        f"""
    <div style="display:none" id="{div_id}">
        <iframe src="javascript: \
            var script = document.createElement('script'); \
            script.type = 'text/javascript'; \
            script.text = {html.escape(repr(source))}; \
            var div = window.parent.document.getElementById('{div_id}'); \
            div.appendChild(script); \
            div.parentElement.parentElement.parentElement.style.display = 'none'; \
        "/>
    </div>
    """,
        unsafe_allow_html=True,
    )


def screenshot_window() -> None:
    # JS Code to be executed
    source = """
// Function to detect if the current browser is Chrome
const isChrome = () => /Chrome/.test(navigator.userAgent) && /Google Inc/.test(navigator.vendor);

const button = document.getElementById('reportButton');
button.addEventListener('click', function() {
    // Alert and exit if the browser is Chrome
    if (isChrome()) {
        //alert("Currently this function is available only on Firefox!");
        //button.style.display = 'none'; // Hides the button
        //return;
    }

    // Load a script dynamically and execute a callback after loading
    const loadScript = (url, isLoaded, callback) => {
        if (!isLoaded()) {
            const script = document.createElement('script');
            script.type = 'text/javascript';
            script.onload = callback;
            script.src = url;
            document.head.appendChild(script);
        } else {
            callback();
        }
    };

    // Check if html2canvas library is loaded
    const isHtml2CanvasLoaded = () => typeof html2canvas !== 'undefined';

    // Capture an individual iframe and call a callback with the result
    const captureIframe = (iframe, callback) => {
        try {
            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            html2canvas(iframeDoc.body, {
                scale: 1,
                logging: true,
                useCORS: true,
                allowTaint: true
            }).then(canvas => {
                callback(canvas ? canvas : null);
            }).catch(error => {
                console.error('Could not capture iframe:', error);
                callback(null);
            });
        } catch (error) {
            console.error('Could not access iframe:', error);
            callback(null);
        }
    };

    // Main function to capture all windows
    const captureAllWindows = () => {
        const streamlitDoc = window.parent.document;
        const stApp = streamlitDoc.querySelector('.main > .block-container');
        const iframes = Array.from(stApp.querySelectorAll('iframe'));
        let capturedImages = [];

        // Process each iframe sequentially
        const processIframes = (index = 0) => {
            if (index < iframes.length) {
                captureIframe(iframes[index], function(canvas) {
                    if (canvas) {
                        const img = document.createElement('img');
                        img.src = canvas.toDataURL('image/png');
                        capturedImages.push({iframe: iframes[index], img: img});
                    } else {
                        console.error('Skipping an iframe due to capture failure.');
                    }
                    processIframes(index + 1);
                });
            } else {
                // Capture the main app window after processing all iframes
                html2canvas(stApp, {
                    onclone: function(clonedDocument) {
                        const clonedIframes = Array.from(clonedDocument.querySelectorAll('iframe'));
                        capturedImages.forEach(({img}, index) => {
                            if (index < clonedIframes.length) {
                                const clonedIframe = clonedIframes[index];
                                clonedIframe.parentNode.replaceChild(img, clonedIframe);
                            }
                        });
                    },
                    scale: 1,
                    logging: true,
                    useCORS: true,
                    allowTaint: true,
                    ignoreElements: () => {}
                }).then(finalCanvas => {
                    // Create a download link for the captured image
                    finalCanvas.toBlob(blob => {
                        const url = window.URL.createObjectURL(blob);
                        var link = document.createElement('a');
                        link.style.display = 'none';
                        link.href = url;
                        link.download = 'screenshot.png';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        window.URL.revokeObjectURL(url);
                    });
                }).catch(error => {
                    console.error('Screenshot capture failed:', error);
                });
            }
        };

        processIframes();
    };

    loadScript(
        'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.3.2/html2canvas.min.js',
        isHtml2CanvasLoaded,
        captureAllWindows
    );
});
"""

    inject_js_code(source=source)


def add_reportgen_button():
    st.markdown(
        """
        <button id="reportButton" class="st-style-button">Generate Page Report</button>

        <style>
        .st-style-button {
            display: inline-flex;
            -webkit-box-align: center;
            align-items: center;
            -webkit-box-pack: center;
            justify-content: center;
            font-weight: 400;
            padding: 0.25rem 0.75rem;
            border-radius: 0.5rem;
            min-height: 38.4px;
            margin: 0px;
            line-height: 1.6;
            color: inherit;
            width: auto;
            user-select: none;
            background-color: white; /* Set a white background */
            border: 1px solid rgba(49, 51, 63, 0.2);
            outline: none; !important
            box-shadow: none !important;
        }

        /* Change background on mouse-over */
        .st-style-button:hover {
            background-color: white;
            color: #0A04D2;
            border: 1px solid #0A04D2;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
    screenshot_window()


def about():
    st.title('Tentang Web App')
    st.write("""
    Web App ini adalah Web yang dapat digunakan sebagai Skor Simulator yang mengambil data dari klasemen Premier League musim 2024/2025.
    Data yang digunakan diambil dari [www.transfermarkt.co.id](https://www.transfermarkt.co.id/premier-league/tabelle/wettbewerb/GB1).
    """)
    st.write("""
    Web App ini juga menyediakan fitur pendaftaran dan pengunduran diri fans Manchester United.
    Fans yang mendaftar akan mendapatkan PDF berisi data diri dan alasan pendaftaran/pengunduran diri.
    Namun, fans klub lain tetap dapat mengisi dan mengunduh PDF, namun dengan syarat harus memilih klub Manchester United.
    """)
    st.write("""
    Web App ini dibuat oleh [Fillah Alamsyah](https://www.github.com/FillahAlamsyah) menggunakan bahasa pemrograman Python dan library Streamlit.
    """)
    st.warning("""Disclaimer: Web App ini hanya untuk keperluan belajar dan tidak untuk tujuan komersial.
               Selain itu, Web App ini tidak berafiliasi dengan klub sepakbola manapun.
               Hanya untuk keperluan belajar dan hiburan. Terima kasih.
    """, icon='⚠️')
    
    st.header('Referensi',divider=True)
    st.subheader('Referensi Web')
    st.markdown("""
    - [Streamlit](https://www.streamlit.io/)
    - [Pandas](https://pandas.pydata.org/)
    - [FPDF](https://pyfpdf.readthedocs.io/en/latest/)
    - [PDF2Image](https://pypi.org/project/pdf2image/)
    """)
    st.subheader('Referensi Gambar')
    st.markdown("[Postingan Threads](https://www.threads.net/@abbkusman_/post/C_0Q8qfspTr?xmt=AQGz-ygaEFsELioTBr2CoTBHXSloQPPbDl_WWkizYOzZlQ)")

    st.image('sources\MU-Southampton.jpeg', caption='Threads', use_column_width=True)
    st.markdown("[Post On Instagram](https://www.instagram.com/p/DAiJA0hSZu4/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==)")
    st.image('sources\Surat-Pengunduran-Diri.jpeg', caption='Postingan Instagram', use_column_width=True)
@st.cache_data
def read_data(file,sheet_name='Sheet1'):
    data = pd.read_excel(file,sheet_name=sheet_name)
    return data
if 'df' not in st.session_state:
    st.session_state.df = read_data('EPL_Data.xlsx')
df = st.session_state.df
# nama_lengkap_klub = ['Liverpool',
#                         'Manchester City',
#                         'Arsenal',
#                         'Chelsea',
#                         'Aston Villa',
#                         'Fulham',
#                         'Newcastle United',
#                         'Spurs',
#                         'Brighton & Hove Albion',
#                         'Nottingham Forest',
#                         'Bournemouth',
#                         'Brentford',
#                         'Manchester United',
#                         'West Ham United',
#                         'Ipwich Town',
#                         'Everton',
#                         'Leicester City',
#                         'Crystal Palace',
#                         'Southampton',
#                         'Wolverhampton Wanderers']

# df['Nama Lengkap Klub'] = nama_lengkap_klub
# pindahkan kolom 'Nama Lengkap Klub' ke posisi kedua
def download_image_from_url(df, column_name):
    for index, row in df.iterrows():
        url = row[column_name]
        file_name = f'{df["Nama Klub"][index]}.svg'
        urllib.request.urlretrieve(url, file_name)
    return df

#download_image_from_url(df, 'Logo')

def logo_club(klub):
    logo_club = df[df['Nama Lengkap Klub'] == klub]['Nama Klub'].values[0]
    path = f'Logopng/{logo_club}.png'
    return path


def data_klasemen():
    st.header('Data Klasemen')
    st.info('Data klasemen Premier League musim 2024/2025 06/10/24', icon='ℹ️')
    st.data_editor(df,
                column_config={
                    "Logo": st.column_config.ImageColumn("Preview Image", help="Streamlit app preview screenshots"),
                    },
        hide_index=True,#use_container_width=True,
        height=700,
    )
    st.info('Referensi [www.transfermarkt.co.id](https://www.transfermarkt.co.id/premier-league/tabelle/wettbewerb/GB1)', icon='ℹ️')

def simulator():
    st.header('Simulator Skor')
    # Membuat Skor Simulator dengan input nama klub dan skor
    with st.expander('Setting'):
        st.info('Simulator Skor Pertandingan', icon='ℹ️')
        sides = st.columns(2)
        klub1 = sides[0].selectbox('Klub 1', df['Nama Lengkap Klub'].unique(), index=18, key='klub1')
        klub2 = sides[1].selectbox('Klub 2', df['Nama Lengkap Klub'].unique(), index=12, key='klub2')
        skor1 = sides[0].number_input('Skor Klub 1', min_value=0, value=0, key='skor1')
        skor2 = sides[1].number_input('Skor Klub 2', min_value=0, value=901, key='skor2')
        goal_scorer1 = sides[0].text_input('Pencetak Gol', help='Masukkan nama pemain yang mencetak gol',
                                        value="Onana (OG) 1'")
        goal_scorer2 = sides[1].text_input('Pencetak Gol ', help='Masukkan nama pemain yang mencetak gol',
                                        value='''Antony 1', 2', 3', 4', 5', 6', 7',8', 9', 10',11', 12', 13', 14', 15', 16', 17', 18', 19', 20', 21', 22', 23', 24', 25', 26', 27', 28', 29', 30', 31', 32', 33', 34', 35', 36', 37', 38', 39', 40', 41', 42', 43', 44', 45', 46', 47', 48', 49', 50', 51', 52', 53', 54', 55', 6', 57', 58', 59', 60', 61', 62', 63', 64', 65', 66', 67', 68', 69', 70', 71', 72', 73', 74', 75', 76', 77', 78', 79', 80', 81', 82', 83', 84', 85', 86', 87', 88', 89', 90'...x100' ''')

    cols = st.columns(5)
    cols[0].image(f'{logo_club(klub1)}', use_column_width=True)
    cols[0].markdown(f"<div style='text-align: center; font-size: 1.25rem;'>{klub1}</div>", unsafe_allow_html=True)
    cols[1].markdown(f"<div style='text-align: center; font-size: 5.625rem;'>{skor1}</div>", unsafe_allow_html=True)
    cols[2].markdown(f"<div style='text-align: center; font-size: 5.625rem;'>-</div>", unsafe_allow_html=True)
    cols[2].markdown(f"<div style='text-align: center; font-size: 1.25rem;'>Full Time</div>", unsafe_allow_html=True)
    cols[3].markdown(f"<div style='text-align: center; font-size: 5.625rem;'>{skor2}</div>", unsafe_allow_html=True)
    cols[4].image(f'{logo_club(klub2)}', use_column_width=True)
    cols[4].markdown(f"<div style='text-align: center; font-size: 1.25rem;'>{klub2}</div>", unsafe_allow_html=True)

    scorer_cols=st.columns(3)
    #Scorer
    scorer_cols[0].markdown(f"<div style='text-align: center; font-size: 1.2rem; margin-top: 1.25rem;'>{goal_scorer1}</div>", unsafe_allow_html=True)
    scorer_cols[1].markdown(f"<div style='text-align: center; font-size: 2.5rem; margin-top: 1.25rem;'>⚽️</div>", unsafe_allow_html=True)
    scorer_cols[2].markdown(f"<div style='text-align: center; font-size: 1.2; margin-top: 1.25rem;'>{goal_scorer2}</div>", unsafe_allow_html=True)

    # Save to Image this page
    #st.subheader('Simpan Skor',divider=True)
    # Tambahkan tombol untuk mengunduh gambar
    #add_reportgen_button()



def create_form_pdf(nama, umur, email, alasan, klub, jenis="Pendaftaran") -> bytes:
    text = "Pendaftaran" if jenis == "Pendaftaran" else "Pengunduran Diri"
    pdf = FPDF(format='A4', unit='mm')
    pdf.add_page()
    # make A4 size paper
    pdf.set_auto_page_break(auto=True, margin=15)

    #tambahkan logo klub di pojok kiri atas
    path = logo_club(klub)
    pdf.image(path, x=10, y=8, w=25)
    # Set font
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 25, f"{text} Fans {klub}", ln=True, align="C")

    # Set font untuk isi
    pdf.set_font("Arial", size=12)

    pdf.ln(10)  # Spasi vertikal

    pdf.cell(200, 10, f"Nama: {nama}", ln=True)
    pdf.cell(200, 10, f"Umur: {umur}", ln=True)
    pdf.cell(200, 10, f"Email: {email}", ln=True)
    pdf.cell(200, 10, f"Klub Favorit: {klub}", ln=True)
    pdf.cell(200, 10, f"Alasan melakukan {text} :", ln=True)
    pdf.multi_cell(200, 10, alasan)

    #tanda tangani
    pdf.ln(10)
    waktu = "Di Tempat, " + pd.Timestamp.now().strftime("%d %B %Y")
    pdf.set_x(-pdf.get_string_width(waktu) - 60)
    pdf.cell(0, 10, f"{waktu}", ln=True, align='R')
    pdf.ln(20)
    pdf.set_x(-pdf.get_string_width("TTD") - 60)
    pdf.cell(0, 10, "TTD", ln=True, align='C')

    # Simpan PDF
    pdf_file = pdf.output(dest='S').encode("latin1")
    return pdf_file

def pendaftaran_fans():
    st.header('Pendaftaran Fans')
    # Input data fans baru dan outputnya berupa pdf dan ditampilkan di streamlit
    nama = st.text_input('Nama',help='Masukkan nama lengkap Anda', placeholder='Masukkan nama lengkap Anda')
    umur = st.number_input('Umur (Tahun)', min_value=0, max_value=100, value=20, placeholder='Masukkan umur Anda', help='Masukkan umur Anda')
    email = st.text_input('Email', help='Masukkan email yang valid', placeholder='Masukkan email yang valid')
    klub = st.selectbox('Nama Klub', df['Nama Lengkap Klub'].unique(), index=12, key='klub_favorit')
    if klub != 'Manchester United':
        st.warning('Maaaf, hanya fans Manchester United yang bisa mendaftar')

    alasan = st.text_area('Alasan')

    pdf_file = create_form_pdf(nama, umur, email, alasan, klub, jenis="Pendaftaran")
    def save_pdf_to_buffer(pdf):
        buffer = io.BytesIO()
        # Write PDF ke buffer
        buffer.write(pdf)
        buffer.seek(0)
        return buffer

    # Menampilkan PDF di Streamlit sebagai gambar
    pdf_viewer(input=pdf_file, render_text=True)
    # Simpan ke buffer
    buffer = save_pdf_to_buffer(pdf_file)
    # Menampilkan PDF dengan opsi unduh
    st.download_button(
        label="Download PDF",
        data=buffer,
        file_name=f"{nama}_registration.pdf",
        mime="application/pdf"
    )



def pengunduran_diri_fans():
    st.header('Pengunduran Diri Fans')
    # Input data fans baru dan outputnya berupa pdf dan ditampilkan di streamlit
    nama = st.text_input('Nama',help='Masukkan nama lengkap Anda', placeholder='Masukkan nama lengkap Anda')
    umur = st.number_input('Umur (Tahun)', min_value=0, max_value=100, value=20, placeholder='Masukkan umur Anda', help='Masukkan umur Anda')
    email = st.text_input('Email', help='Masukkan email yang valid', placeholder='Masukkan email yang valid')
    klub = st.selectbox('Nama Klub', df['Nama Lengkap Klub'].unique(), index=12, key='klub_favorit')
    if klub != 'Manchester United':
        st.warning('Maaaf, hanya fans Manchester United yang bisa mendaftar')

    alasan = st.text_area('Alasan')
    pdf_file = create_form_pdf(nama, umur, email, alasan, klub, jenis="Pengunduran Diri")
    def save_pdf_to_buffer(pdf):
        buffer = io.BytesIO()
        # Write PDF ke buffer
        buffer.write(pdf)
        buffer.seek(0)
        return buffer

    # Menampilkan PDF di Streamlit sebagai gambar
    pdf_viewer(input=pdf_file, render_text=True)
    # Simpan ke buffer
    buffer = save_pdf_to_buffer(pdf_file)
    # Menampilkan PDF dengan opsi unduh
    st.download_button(
        label="Download PDF",
        data=buffer,
        file_name=f"{nama}_resignation.pdf",
        mime="application/pdf"
    )

page1 = st.Page(page=about, title='Tentang Web App')
page2 = st.Page(page=simulator, title='Simulator Skor')
page3 = st.Page(page=data_klasemen, title='Data Klasemen')
page4 = st.Page(page=pendaftaran_fans, title='Pendaftaran Fans')
page5 = st.Page(page=pengunduran_diri_fans, title='Pengunduran Diri Fans')

page = st.navigation([
    page1,
    page2,
    page3,
    page4,
    page5
])
page.run()