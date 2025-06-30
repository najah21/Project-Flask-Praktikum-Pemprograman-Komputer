from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv
import os
import pymysql

# Konfigurasi driver MySQL
pymysql.install_as_MySQLdb()

# Load variabel dari file .env (jika ada)
load_dotenv()

app = Flask(__name__)
CORS(app)

# Konfigurasi database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'mysql://root:@localhost/penjualan.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inisialisasi database
db = SQLAlchemy(app)

# Model database
class Penjualan(db.Model):
    __tablename__ = "penjualan"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama_pembeli = db.Column(db.String(100), nullable=False)
    nama_barang = db.Column(db.String(255), nullable=False)
    tanggal_jual = db.Column(db.Date, nullable=True)
    jumlah_barang = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nama_pembeli": self.nama_pembeli,
            "nama_barang": self.nama_barang,
            "tanggal_jual": str(self.tanggal_jual) if self.tanggal_jual else None,
            "jumlah_barang": self.jumlah_barang
        }

# Bikin tabel saat pertama kali dijalankan
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/penjualan', methods=['GET'])
def get_penjualan():
    penjualan = Penjualan.query.all()
    return jsonify([p.to_dict() for p in penjualan])

@app.route('/penjualan/<int:id>', methods=['GET'])
def get_penjualan_by_id(id):
    penjualan = db.session.get(Penjualan, id)
    if not penjualan:
        return jsonify({"message": "Data penjualan tidak ditemukan"}), 404
    return jsonify(penjualan.to_dict())

@app.route('/penjualan', methods=['POST'])
def add_penjualan():
    try:
        data = request.get_json()
        
        if not all(k in data for k in ("nama_pembeli", "nama_barang", "tanggal_jual", "jumlah_barang")):
            return jsonify({"error": "Data tidak lengkap"}), 400
        if not isinstance(data["jumlah_barang"], int) or data["jumlah_barang"] <= 0:
            return jsonify({"error": "Jumlah barang harus berupa angka positif"}), 400
        
        penjualan = Penjualan(
            nama_pembeli=data["nama_pembeli"],
            nama_barang=data["nama_barang"],
            tanggal_jual=datetime.strptime(data["tanggal_jual"], "%Y-%m-%d").date() if data["tanggal_jual"] else None,
            jumlah_barang=data["jumlah_barang"]
        )
        
        db.session.add(penjualan)
        db.session.commit()

        return jsonify({"message": "Data penjualan berhasil ditambahkan", "data": penjualan.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/penjualan/<int:id>', methods=['PUT'])
def update_penjualan(id):
    penjualan = db.session.get(Penjualan, id)
    if not penjualan:
        return jsonify({"message": "Data penjualan tidak ditemukan"}), 404

    try:
        data = request.get_json()
        
        if "jumlah_barang" in data and (not isinstance(data["jumlah_barang"], int) or data["jumlah_barang"] <= 0):
            return jsonify({"error": "Jumlah barang harus berupa angka positif"}), 400
        
        penjualan.nama_pembeli = data.get("nama_pembeli", penjualan.nama_pembeli)
        penjualan.nama_barang = data.get("nama_barang", penjualan.nama_barang)
        penjualan.tanggal_jual = datetime.strptime(data["tanggal_jual"], "%Y-%m-%d").date() if data.get("tanggal_jual") else penjualan.tanggal_jual
        penjualan.jumlah_barang = data.get("jumlah_barang", penjualan.jumlah_barang)
        
        db.session.commit()
        return jsonify({"message": "Data penjualan diperbarui", "data": penjualan.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/penjualan/<int:id>', methods=['DELETE'])
def delete_penjualan(id):
    penjualan = db.session.get(Penjualan, id)
    if not penjualan:
        return jsonify({"message": "Data penjualan tidak ditemukan"}), 404
    
    try:
        db.session.delete(penjualan)
        db.session.commit()
        return jsonify({"message": "Data penjualan dihapus"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Run server
if __name__ == '__main__':
    app.run(debug=True)
