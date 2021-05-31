import sys
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QLabel, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMessageBox

import requests
import json
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("welcomescreen.ui",self)
        self.bg.setPixmap(QPixmap('bg.jpg'))
        self.login.clicked.connect(self.gotologin)
        self.create.clicked.connect(self.gotocreate)

    def gotologin(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotocreate(self):
        create = CreateAccScreen()
        widget.addWidget(create)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("login.ui",self)
        self.bgl.setPixmap(QPixmap('bg.jpg'))
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.loginfunction)

    def loginfunction(self):
        user = self.emailfield.text()
        password = self.passwordfield.text()

        if len(user)==0 or len(password)==0:
            self.error.setText("Please input all fields.")

        else:
            self.error.setText("Logging in...")
            res = requests.post("https://ekms-api.herokuapp.com/login", data={
                "email" : user,
                "password": password
            })
            json = res.json()
            # currenLogged = json['userId']
            if res.status_code == 200:
                print("Successfully logged in.")
                if json["level"] == "kader":
                    cekkms = CekKMS()
                    widget.addWidget(cekkms)
                    widget.setCurrentIndex(widget.currentIndex()+1)

                else:
                    self.worker = WorkerLogin(json["userId"])
                    self.worker.start()
                    self.worker.isdone.connect(self.openmenu)
                
            else:
                self.error.setText("Invalid username or password")
    def openmenu(self,id):
        menuscreen = Menu(id)
        widget.addWidget(menuscreen)
        widget.setCurrentIndex(widget.currentIndex()+1)

class CreateAccScreen(QDialog):
    def __init__(self):
        super(CreateAccScreen, self).__init__()
        loadUi("createacc.ui",self)
        self.bgs.setPixmap(QPixmap('bg.jpg'))
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpasswordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signup.clicked.connect(self.signupfunction)

    def signupfunction(self):
        user = self.emailfield.text()
        password = self.passwordfield.text()
        confirmpassword = self.confirmpasswordfield.text()

        if len(user)==0 or len(password)==0 or len(confirmpassword)==0:
            self.error.setText("Please fill in all inputs.")

        elif password!=confirmpassword:
            self.error.setText("Passwords do not match.")
        else:
            res = requests.post("https://ekms-api.herokuapp.com/register", data={
                "email": user,
                "password": password
            })
            if res:
                print("Successfully create account.")
                menuscreen = Menu()
                widget.addWidget(menuscreen)
                widget.setCurrentIndex(widget.currentIndex()+1)
            else:
                self.error.setText("Gagal Membuat Akun!")

class WorkerLogin(QThread):
    # ortu = pyqtSignal(dict)
    isdone = pyqtSignal(str)

    def __init__(self,id):
        super(WorkerLogin, self).__init__()
        self.id = id

    def run(self):
        ortujson = requests.get("https://ekms-api.herokuapp.com/ortus/userId/"+self.id).json()[0]
        balitajson = requests.get("https://ekms-api.herokuapp.com/balitas/userId/"+self.id).json()[0]
        # self.ortu.emit(ortujson)
        self.isdone.emit(ortujson["userId"])
        print("iyei")
        data = {
            "ortu": ortujson,
            "balita": balitajson
        }
        with open('data.json', 'w') as outfile:
            json.dump(data, outfile)
        

class Menu(QDialog):
    def __init__(self,id):
        super(Menu, self).__init__()
        loadUi("menu.ui",self)
        self.id = id
        self.ortu = {}
        self.balita = {}
        self.getdata()
        
        self.profile.clicked.connect(self.gotoprofile)
        self.imunisasi.clicked.connect(self.gotoimunisasi)
        self.grafik.clicked.connect(self.gotografik)
        self.logout.clicked.connect(self.gologout)
        self.pprofile.setPixmap(QPixmap('profile.png'))
        self.pimunisasi.setPixmap(QPixmap('imunisasi.png'))
        self.pgrafik.setPixmap(QPixmap('grafik.png'))

    def getdata(self):
        with open('data.json') as json_file:
            data = json.load(json_file)
            self.ortu = data["ortu"]
            self.balita = data["balita"]
            print(data)

    def gotoprofile(self):
        profile = Profile(self.ortu,self.balita)
        widget.addWidget(profile)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotoimunisasi(self):
        imunisasi = Imunisasi(self.id)
        widget.addWidget(imunisasi)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotografik(self):
        grafik = Grafik(self.id,self.balita)
        widget.addWidget(grafik)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gologout(self):
        print("Log out Success")
        out = LoginScreen()
        widget.addWidget(out)
        widget.setCurrentIndex(widget.currentIndex()+1)

class Profile(QDialog):
    def __init__(self,ortu,balita):
        super(Profile, self).__init__()
        loadUi("profileortu.ui",self)
        self.balita = balita
        self.ortu = ortu
        self.profilebayi.clicked.connect(self.gotoprofilebayi)
        self.btnbalik.clicked.connect(self.balikk)
        
        # kalo mau isi langsung pake setText()
        # ku isi buat test
        t = "test"
        # res = requests.get("https://ekms-api.herokuapp.com/ortus/userId/"+self.id)
        # json = res.json()[0]
        nama_ayah = self.nama_ayah.setText(ortu["ayah"]["nama"])
        nik_ayah = self.nik_ayah.setText(ortu["ayah"]["nik"])
        nama_ibu = self.nama_ibu.setText(ortu["ibu"]["nama"])
        nik_ibu = self.nik_ibu.setText(ortu["ibu"]["nik"])
        alamat = self.alamat.setText(ortu["alamat"])
        telp = self.telp.setText(ortu["telp"])
        
    def gotoprofilebayi(self):
        pbayi = ProfileBayi(self.ortu,self.balita)
        widget.addWidget(pbayi)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def balikk(self):
        balikkk = Menu(self.ortu["userId"])
        widget.addWidget(balikkk)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
class Grafik(QDialog):
    def __init__(self,id,balita):
        super(Grafik, self).__init__()
        loadUi("grafik.ui",self)
        self.id = id
        self.balita = balita
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.grafik()
        self.kembalik.clicked.connect(self.balik2)

    def grafik(self):
        bulan = list(self.balita["berat"].keys())
        berat = list(self.balita["berat"].values())
        print(berat)
        # create an axis
        ax = self.figure.add_subplot(111)

        # discards the old graph
        ax.clear()

        # plot data
        ax.plot(berat, '*-')

        # refresh canvas
        self.canvas.draw()
        # plt.plot(bulan, berat, color='red', marker='o')
        # plt.title('Perkembangan Berat Balita', fontsize=14)
        # plt.xlabel('Bulan', fontsize=14)
        # plt.ylabel('Berat', fontsize=14)
        # plt.grid(True)
        # plt.show()


    def balik2(self):
        balike = Menu(self.id)
        widget.addWidget(balike)
        widget.setCurrentIndex(widget.currentIndex()+1)


class Imunisasi(QDialog):
    def __init__(self,id):
        super(Imunisasi, self).__init__()
        loadUi("imunisasi.ui",self)
        self.id = id
        self.btncampak.clicked.connect(self.gotocampak)
        self.btnvarisela.clicked.connect(self.gotovarisela)
        self.btnhepatitis.clicked.connect(self.gotohepatitis)
        self.btnpolio.clicked.connect(self.gotopolio)

        self.pcampak.setPixmap(QPixmap('campak.png'))
        self.pvarisela.setPixmap(QPixmap('varisela.png'))
        self.phepatitis.setPixmap(QPixmap('hepatitis.png'))
        self.ppolio.setPixmap(QPixmap('polio.png'))

    def gotocampak(self):
        campak = DaftarImunisasi("campak",self.id)
        widget.addWidget(campak)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotovarisela(self):
        varisela = DaftarImunisasi("varisela",self.id)
        widget.addWidget(varisela)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotohepatitis(self):
        hepatitis = DaftarImunisasi("hepatitis",self.id)
        widget.addWidget(hepatitis)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotopolio(self):
        polio = DaftarImunisasi("polio",self.id)
        widget.addWidget(polio)
        widget.setCurrentIndex(widget.currentIndex()+1)


class ProfileBayi(QDialog):
    def __init__(self,ortu,balita):
        super(ProfileBayi, self).__init__()
        loadUi("profilebalita.ui",self)
        self.ortu = ortu
        self.balita = balita
        self.kembalii.clicked.connect(self.kembaliii)
        self.pbayi.setPixmap(QPixmap('baby.png'))
        self.kembalii.clicked.connect(self.kembaliii)
        # kalo mau isi langsung pake setText()
        # ku isi buat test aja
        nama_balita = self.nama_balita.setText(balita["nama"])
        usia_balita = self.usia_balita.setText(str(balita["umur"]))
        tanggal_lahir = self.tanggal_lahir.setText(str(balita["tglLahir"]))
        jenis_kelamin = self.jenis_kelamin.setText(balita["jk"])

    def kembaliii(self):
        kem = Profile(self.ortu, self.balita)
        widget.addWidget(kem)
        widget.setCurrentIndex(widget.currentIndex()+1)

class DaftarImunisasi(QDialog):
    def __init__(self,tipe,id):
        super(DaftarImunisasi, self).__init__()
        loadUi("daftarimunisasi.ui",self)
        self.id = id
        self.tipe = tipe
        self.daftarimun.clicked.connect(self.daftarImunisasi)

    def daftarImunisasi(self):
        tanggal_imunisasi = self.tanggal_imunisasi.text()
        jam = self.jam.text()
        res = requests.post("https://ekms-api.herokuapp.com/imunisasi/"+self.id, data={
            "tipe" : self.tipe,
            "jam" : jam,
            "tanggal" :tanggal_imunisasi
        })
        if res:
            widget.addWidget(AlertImun(self.id))
            widget.setCurrentIndex(widget.currentIndex()+1)
        else:
            print("Gagal")

class Search(QDialog):
    def __init__(self):
        super(Search, self).__init__()
        loadUi("search.ui",self)
        tsearch = self.tsearch.text()
    #     self.bsearch.clicked.connect(self.gotosearch)

    # def gotosearch(self):
    #     lama = Lama()
    #     widget.addWidget(lama)
    #     widget.setCurrentIndex(widget.currentIndex()+1)
        self.bsearch.clicked.connect(self.gotobulanan)

    def gotobulanan(self):
        bulanan = DataBulanan()
        widget.addWidget(bulanan)
        widget.setCurrentIndex(widget.currentIndex()+1)


class CekKMS(QDialog):
    def __init__(self):
        super(CekKMS, self).__init__()
        loadUi("cekekms.ui",self)
        self.blama.clicked.connect(self.gotolama)
        self.bbaru.clicked.connect(self.gotobaru)
        self.logoutt.clicked.connect(self.gologoutt)

    def gotolama(self):
        lama = Search()
        widget.addWidget(lama)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotobaru(self):
        baru = Baru()
        widget.addWidget(baru)
        widget.setCurrentIndex(widget.currentIndex() + 1)   

    def gologoutt(self):
        outt = LoginScreen()
        widget.addWidget(outt)
        widget.setCurrentIndex(widget.currentIndex()+1)


class DataBulanan(QDialog):
    def __init__(self):
        super(DataBulanan, self).__init__()
        loadUi("inputdatabulananbalita.ui",self)
        nama_balita = self.nama_balita.text()
        # ntah apa pake buat dropdown
        umur_balita = self.umur_balita.currentText()
        tinggi_badan = self.tinggi_badan.text()
        kenaikan_tinggi = self.kenaikan_tinggi_badan.text()
        berat_badan = self.tinggi_badan.text()
        kenaikan_berat = self.kenaikan_berat_badan.text()

        self.bkonfirmasi.clicked.connect(self.konfirmasibulanan)

    def konfirmasibulanan(self):

        konfirm = AlertBerhasil()
        widget.addWidget(konfirm)
        widget.setCurrentIndex(widget.currentIndex()+1)
        


class Baru(QDialog):
    def __init__(self):
        super(Baru, self).__init__()
        loadUi("inputdataortu.ui",self)
        self.signup.clicked.connect(self.registerortu)

    def registerortu(self):
        nama_ayah = self.nama_ayah.text()
        nik_ayah = self.nik_ayah.text()
        nama_ibu = self.nama_ibu.text()
        nik_ibu = self.nik_ibu.text()
        alamat = self.alamat.text()
        telp = self.telp.text()

        res = requests.post("https://ekms-api.herokuapp.com/ortubaru", json={
            "alamat": alamat,
            "telp": telp,
            "ayah": {
                "nik": nik_ayah,
                "nama": nama_ayah
            },
            "ibu": {
                "nik": nik_ibu,
                "nama": nama_ibu
            },
        })
        
        json = res.json()

        if res:
           print("Berhasil terdaftar")
           print("Email    : "+json["mail"])
           print("Password : "+json["pass"])
           widget.addWidget(InputDataBalita())
           widget.setCurrentIndex(widget.currentIndex()+1)

        else:
            print("Gagal terdaftar")
            self.error.setText("Gagal Daftar Ulangi Lagi!")


class InputDataBalita(QDialog):
    def __init__(self):
        super(InputDataBalita, self).__init__()
        loadUi("inputdatabalita.ui",self)
        self.daftardatabayi.clicked.connect(self.daftarbayi)
        # nama_balita = self.nama_balita.text()
        # umur_balita = self.umur_balita.currentText()
        # tinggi_badan = self.tinggi_badan.text()
        # berat_badan = self.berat_badan.text()
        # nik_balita = self.kenaikan_tinggi_badan.text()
        # jenis_kelamin = self.jenis_kelamin.text()
        # tanggal_lahir = self.tanggal_lahir.text()
        # tanggal_periksa = self.tanggal_periksa.text()

    def daftarbayi(self):
        widget.addWidget(AlertBerhasil())
        widget.setCurrentIndex(widget.currentIndex()+1)

class AlertBerhasil(QDialog):
    def __init__(self):
        super(AlertBerhasil, self).__init__()
        loadUi("alertbulanan.ui",self)
        self.bkembali.clicked.connect(self.back)


    def back(self):
        widget.addWidget(CekKMS())
        widget.setCurrentIndex(widget.currentIndex()+1)

class AlertBaru(QDialog):
    def __init__(self):
        super(AlertBaru, self).__init__()
        loadUi("alertbaru.ui",self)
        self.btnkembali.clicked.connect(self.backk)
        self.semail.setText("Email    : ")
        self.spass.setText("Password : ")

    def backk(self):
        widget.addWidget(CekKMS())
        widget.setCurrentIndex(widget.currentIndex()+1)

class AlertImun(QDialog):
    def __init__(self,id):
        super(AlertImun, self).__init__()
        loadUi("alertimun.ui",self)
        self.id = id
        self.balikmun.clicked.connect(self.balikimun)

    def balikimun(self):
        widget.addWidget(Menu(self.id))
        widget.setCurrentIndex(widget.currentIndex()+1)


# 1235@gmail.com
# 5ahx3d

# main
app = QApplication(sys.argv)
welcome = WelcomeScreen()
widget = QtWidgets.QStackedWidget()
# widget = QtWidgets.QStackedWidget()
widget.addWidget(welcome)
widget.setFixedHeight(700)
widget.setFixedWidth(1150)
widget.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")