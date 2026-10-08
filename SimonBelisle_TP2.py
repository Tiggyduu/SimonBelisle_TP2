from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton, QCheckBox, QMessageBox
from maya import cmds
import json
 
class MessageBoard(QWidget): # QWidget est la classe mère et MessageBoard hérite de ses composantes
    def __init__(self): # Constructeur
        super().__init__() # Constructeur du parent QWidget (super = superclass (classe supérieure))
        self.setWindowTitle("Outliner organizer") 
        self.create_ui()

    def create_ui(self):
        # Crée le box layout
        layout = QVBoxLayout(self)
        label = QLabel("Enter JSON rule path:")
        layout.addWidget(label)

        # Ajoute la QLineEdit pour entrer le chemin du fichier JSON
        self.text = QLineEdit()
        self.text.setPlaceholderText("JSON rule path...")
        layout.addWidget(self.text)

        # Ajoute les QCheckBox
        self.checkbox1 = QCheckBox("Apply on selection only")
        self.checkbox2 = QCheckBox("Apply colors")
        self.checkbox3 = QCheckBox("Apply reorder")
        layout.addWidget(self.checkbox1)
        layout.addWidget(self.checkbox2)
        layout.addWidget(self.checkbox3)

        # Ajoute le QPushButton pour organiser l'outliner
        self.button = QPushButton("Organize outliner")
        layout.addWidget(self.button)
        self.button.clicked.connect(self.apply_on_click)

        # Change la taille de la fenêtre
        self.resize(400, 100)

    def load_json(self, path):
        # Cette ligne corrige un problème que j'avais avec le chemin d'accès
        path = path.replace('\\', '/')

        # Load le fichier JSON
        try:
            with open(path, 'r') as json_file:
                self.rules = json.load(json_file)
            print("Loading JSON from path:", path)
            return True
        # Affiche un Warning si le fichier JSON n'est pas accessible
        except:
            QMessageBox.warning(self, "Warning", "Could not load JSON file")
            return False

    def apply_on_click(self):
        print("Organize")

        # Load le fichier JSON à partir du chemin et vérifie si le fichier est accessible
        if not self.load_json(self.text.text()):
            return

        # La sélection ets vide pas défaut pour que je puisse facilement vérifier dans mes autres fonctions si la sélection est vide ou non
        selection = None
        # La sélection vide devient la sélection maya si le checkbox est coché
        if self.checkbox1.isChecked():
            print("Apply on selection only")

            # Sélection = sélection maya
            selection = cmds.ls(selection=True, long=True)

            # Affiche un warning si la sélection est vide
            if not selection:
                QMessageBox.warning(self, "Warning", "Nothing is selected.")
                return

        # Maya CTRL+Z (open chunk)
        # Tout ce qui est entre le "open" et le "close" est réversible avec un seul CTRL+Z
        cmds.undoInfo(openChunk=True)

        try:

            if self.checkbox2.isChecked():
                self.apply_colors(selection)

            if self.checkbox3.isChecked():
                self.apply_reorder(selection)

        finally:
            # Maya CTRL+Z (close chunk)
            cmds.undoInfo(closeChunk=True)
        
    def apply_colors(self, selection):
        print("Apply colors")

        # Si rien n'est sélectionné, la sélection devient tout ce qui est dans le outliner (on applique à tous les éléments)
        if selection is None:
            selection = cmds.ls(transforms=True, long=True)

        # On loop à travers chaque éléments du outliner et on applique les couleurs selon les règles du fichier JSON
        for item in selection:
            # Item_name est le nom de l'élément sans le chemin complet (si l'item est groupé)
            item_name = item.split('|')[-1]

            # Verifie si le nom de l'item correspond aux préfixes (keys)
            for prefix, rgb in self.rules.items():
                if item_name.startswith(prefix):
                    try:
                        # Permet de changer la couleur de l'item dans le outliner
                        cmds.setAttr(f"{item}.useOutlinerColor", 1)

                        # Applique la couleur RGB comme dans le fichier JSON
                        cmds.setAttr(f"{item}.outlinerColor", rgb[0], rgb[1], rgb[2])

                    except Exception as err:
                        print(f"Could not apply color to {item}: {err}")
                    break

    def apply_reorder(self, selection):
        print("Apply reorder")

        # Si rien n'est sélectionné, la sélection devient tout ce qui est dans le outliner (on trie tous les éléments)
        if selection is  None:
            selection = cmds.ls(transforms=True, long=True)

        # Prend les keys dans le rules.json
        keys = list(self.rules.keys())

        # Trie chaque élément selon la position de son préfixe dans les keys du rules.json
        sorted_selection = sorted(selection, key=lambda item: next((i for i, p in enumerate(keys) if item.split('|')[-1].startswith(p)), len(keys)))
        
        # Passe à travers la liste à l'envers pour que les éléments soient placés correctement dans le outliner
        for obj in reversed(sorted_selection):
            cmds.reorder(obj, front=True)
            print(f" - Reordered: {obj}")

def main():
    global widget
    try:
        widget.close()
    except Exception:
        pass
    widget = MessageBoard()
    widget.show()
 
main()