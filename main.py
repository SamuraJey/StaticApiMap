from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore
from PyQt5 import uic


import sys
import requests


class MapMain(QWidget):
    def __init__(self):
        super(MapMain, self).__init__()
        uic.loadUi('map.ui', self)

        self.type_of_map.setEditable(True)
        self.type_of_map.lineEdit().setAlignment(QtCore.Qt.AlignCenter)
        self.type_of_map.setEditable(False)

        self.set_map()
        self.findit.clicked.connect(self.set_map)

    def set_map(self):
        self.api_req()

        map_photo = QPixmap(self.map_file)
        map_photo = map_photo.scaled(1100, 800)
        self.map_line.setPixmap(map_photo)

    def api_req(self):
        if self.point_to_find.text() == '':
            latitude = self.latit_inp.text()
            longitude = self.longit_inp.text()
            spn = self.spin.value()

        else:
            point = self.point_to_find.text()
            API_request = f'http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={point}&format=json'
            response = requests.get(API_request)

            json_response = response.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            toponym_coodrinates = toponym["Point"]["pos"]
            latitude, longitude = toponym_coodrinates.split(' ')
            self.latit_inp.setText(latitude)
            self.longit_inp.setText(longitude)
            spn = self.spin.value()

        types = {
            'Режим "Карта"': 'map',
            'Режим "Спутник"': 'sat',
            'Режим "Гибрид"': 'sat,skl'
        }

        API_request = f'https://static-maps.yandex.ru/1.x/?ll={latitude},{longitude}&spn={spn},{spn}&l=' \
                      f'{types[self.type_of_map.currentText()]}&size=650,450&pt={latitude},{longitude},flag'
        response = requests.get(API_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(API_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        else:
            self.map_file = 'map.png'

            with open(self.map_file, 'wb') as file:
                file.write(response.content)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_PageUp:
            spn = self.spin.setValue(self.spin.value() + 0.05)
            self.set_map()
        elif event.key() == QtCore.Qt.Key_PageDown:
            spn = self.spin.setValue(self.spin.value() - 0.05)
            self.set_map()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MapMain()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())