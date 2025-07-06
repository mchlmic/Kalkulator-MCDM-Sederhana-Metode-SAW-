from flask import Flask, render_template, url_for, redirect, request, session

app = Flask(__name__)
app.secret_key = 'secret_key'

@app.route("/")
def home():
    pengunjung = "semua orang"
    return render_template('home.html',)

@app.route("/materi/")
def materi():
    return render_template('materi.html')

@app.route("/kalkulator/")
def kalkulator():
    return render_template('kalkulator.html')


def hitung_preferensi(alternatif, bobot_kriteria):
    n_alternatif = len(alternatif)
    n_kriteria = len(bobot_kriteria)
    
    # Normalisasi bobot kriteria
    total_bobot = sum([bobot for _, bobot in bobot_kriteria])
    bobot_kriteria = [(jenis, bobot/total_bobot) for jenis, bobot in bobot_kriteria]
    
    # Normalisasi matriks alternatif
    normalisasi = []
    for i in range(n_alternatif):
        row = []
        for j in range(n_kriteria):
            jenis_kriteria, bobot = bobot_kriteria[j]
            if jenis_kriteria == "benefit":
                nilai = alternatif[i][j] / max([alternatif[k][j] for k in range(n_alternatif)])
            else:
                nilai = min([alternatif[k][j] for k in range(n_alternatif)]) / alternatif[i][j]
            row.append(nilai)
        normalisasi.append(row)

    # Hitung nilai preferensi
    preferensi = []
    for i in range(n_alternatif):
        hitung_preferensi = [normalisasi[i][j] * bobot_kriteria[j][1] for j in range(n_kriteria)]
        nilai = sum(hitung_preferensi)
        preferensi.append(nilai)
    
    return preferensi

@app.route('/step1/')
def step1():
    return render_template("step1.html")

@app.route('/step2/', methods=['GET', 'POST'])
def step2():
    n_alternatif = 2
    n_kriteria = 2
    if request.method == 'POST':
        n_alternatif = int(request.form['n_alternatif'])
        n_kriteria = int(request.form['n_kriteria'])
        session['n_alternatif'] = n_alternatif
        session['n_kriteria'] = n_kriteria

    return render_template("step2.html", n_alternatif=n_alternatif, n_kriteria=n_kriteria)
        

@app.route('/hasil/', methods=['GET', 'POST'])
def hasil():
    n_alternatif = int(session.get('n_alternatif'))
    n_kriteria = int(session.get('n_kriteria'))
    
    if request.method == 'POST':
        nama_kriteria = []
        for i in range(n_kriteria):
            nama_kriteria.append(request.form[f'nama_kriteria_{i+1}'])       

        nama_alternatif = []
        for i in range(n_alternatif):
            nama_alternatif.append(request.form[f'nama_alternatif_{i+1}'])

        alternatif = []
        for i in range(n_alternatif):
            row = []
            for j in range(n_kriteria):
                nilai = float(request.form[f'alternatif_{i+1}_kriteria_{j+1}'])
                row.append(nilai)
            alternatif.append(row)

        bobot_kriteria = []
        for i in range(n_kriteria):
            jenis_kriteria = request.form[f'jenis_kriteria_{i+1}']
            bobot = float(request.form[f'bobot_kriteria_{i+1}'])
            bobot_kriteria.append((jenis_kriteria, bobot))
        
        total_bobot = sum([bobot for _, bobot in bobot_kriteria])        
        bobot_kriteria = [(jenis, bobot/total_bobot) for jenis, bobot in bobot_kriteria]

        normalisasi = []
        for i in range(n_alternatif):
            row = []
            for j in range(n_kriteria):
                jenis_kriteria, bobot = bobot_kriteria[j]
                if jenis_kriteria == "benefit":
                    nilai = alternatif[i][j] / max([alternatif[k][j] for k in range(n_alternatif)])
                else:
                    nilai = min([alternatif[k][j] for k in range(n_alternatif)]) / alternatif[i][j]
                row.append(nilai)
            normalisasi.append(row)

        hitung_pref = []
        for i in range(n_alternatif):
            hitung = [normalisasi[i][j] * bobot_kriteria[j][1] for j in range(n_kriteria)]
            hitung_pref.append(hitung)   

        preferensi = hitung_preferensi(alternatif, bobot_kriteria)
        hasil = [{"alternatif": f"Alternatif {i+1}", "nilai": nilai} for i, nilai in enumerate(preferensi)]

        # mengambil nilai terbesar dari setiap alternatif
        nilai_terbesar = [x['nilai'] for x in hasil]

        # mengurutkan nilai terbesar secara descending dan mengambil indexnya
        peringkat = sorted(range(len(nilai_terbesar)), key=lambda k: nilai_terbesar[k], reverse=True)

        # menambahkan peringkat pada setiap alternatif
        for i, rank in enumerate(peringkat):
            hasil[rank]['peringkat'] = i+1

        return render_template("hasil.html", hasil=hasil, nama_kriteria=nama_kriteria, nama_alternatif=nama_alternatif, n_alternatif=n_alternatif, 
        n_kriteria=n_kriteria, alternatif=alternatif, bobot_kriteria=bobot_kriteria, preferensi=preferensi, hitung_pref=hitung_pref, peringkat=peringkat)

if __name__ == "__main__":
    app.run(debug=True)