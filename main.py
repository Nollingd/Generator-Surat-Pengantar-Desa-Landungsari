!pip install pyngrok
# Tambahkan ngrok authtoken (GANTI dengan milikmu!)
!ngrok config add-authtoken 2q21bZn5nQFgMwrK59fhSXFqOIB_48NSHVSpNLZtQ4CfjUhz3

from pyngrok import ngrok

# Buat tunnel dengan syntax yang benar:
public_url = ngrok.connect("http://localhost:8501")
print("🌐 Ngrok tunnel:", public_url)

# Jalankan Streamlit (background)
!streamlit run form.py --server.port 8501
