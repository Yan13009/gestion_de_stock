import tkinter as tk
from tkinter import ttk
import mysql.connector

class StockManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion de Stock")

        # Connexion à la base de données
        self.connection = mysql.connector.connect(
            host="localhost",
            user="user",
            password="Azerty13009$",
            database="store"
        )
        self.cursor = self.connection.cursor()

        # Création des tables si elles n'existent pas
        self.create_tables()

        # Création de l'interface graphique
        self.create_gui()

    def create_tables(self):
        # Créer la table "category"
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS category (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(255)
            )
        """)

        # Créer la table "product"
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS product (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(255),
                description TEXT,
                price INT,
                quantity INT,
                id_category INT,
                FOREIGN KEY (id_category) REFERENCES category(id)
            )
        """)

    def create_gui(self):
        # Créer l'interface graphique
        self.tree = ttk.Treeview(self.root, columns=("ID", "Nom", "Description", "Prix", "Quantité", "Catégorie"))
        self.tree.heading("#0", text="")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nom", text="Nom")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Prix", text="Prix")
        self.tree.heading("Quantité", text="Quantité")
        self.tree.heading("Catégorie", text="Catégorie")
        self.tree.pack(padx=10, pady=10)

        # Boutons d'action
        add_button = tk.Button(self.root, text="Ajouter", command=self.add_product)
        add_button.pack(side=tk.LEFT, padx=10)
        delete_button = tk.Button(self.root, text="Supprimer", command=self.delete_product)
        delete_button.pack(side=tk.LEFT, padx=10)
        update_button = tk.Button(self.root, text="Modifier", command=self.update_product)
        update_button.pack(side=tk.LEFT, padx=10)

        # Charger les produits dans l'interface graphique
        self.load_products()

    def load_products(self):
        # Effacer les anciennes entrées
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Récupérer les produits depuis la base de données
        query = """
            SELECT product.id, product.name, product.description, product.price,
                   product.quantity, category.name AS category_name
            FROM product
            LEFT JOIN category ON product.id_category = category.id
        """
        self.cursor.execute(query)
        products = self.cursor.fetchall()

        # Afficher les produits dans l'interface graphique
        for product in products:
            self.tree.insert("", "end", values=product)

    def add_product(self):
        # Interface graphique pour ajouter un produit
        add_window = tk.Toplevel(self.root)
        add_window.title("Ajouter un Produit")

        tk.Label(add_window, text="Nom:").pack()
        name_entry = tk.Entry(add_window)
        name_entry.pack()

        tk.Label(add_window, text="Description:").pack()
        description_entry = tk.Entry(add_window)
        description_entry.pack()

        tk.Label(add_window, text="Prix:").pack()
        price_entry = tk.Entry(add_window)
        price_entry.pack()

        tk.Label(add_window, text="Quantité:").pack()
        quantity_entry = tk.Entry(add_window)
        quantity_entry.pack()

        tk.Label(add_window, text="Catégorie:").pack()
        category_entry = tk.Entry(add_window)
        category_entry.pack()

        add_button = tk.Button(add_window, text="Ajouter", command=lambda: self.insert_product(
            name_entry.get(),
            description_entry.get(),
            price_entry.get(),
            quantity_entry.get(),
            category_entry.get()
        ))
        add_button.pack()

    def insert_product(self, name, description, price, quantity, category):
        # Insérer un nouveau produit dans la base de données
        query = "INSERT INTO product (name, description, price, quantity, id_category) VALUES (%s, %s, %s, %s, %s)"
        category_id = self.get_category_id(category)
        values = (name, description, price, quantity, category_id)
        self.cursor.execute(query, values)
        self.connection.commit()

        # Charger à nouveau les produits dans l'interface graphique
        self.load_products()

    def get_category_id(self, category_name):
        # Récupérer l'ID de la catégorie à partir de son nom
        query = "SELECT id FROM category WHERE name = %s"
        self.cursor.execute(query, (category_name,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            # Si la catégorie n'existe pas, l'ajouter à la base de données
            query = "INSERT INTO category (name) VALUES (%s)"
            self.cursor.execute(query, (category_name,))
            self.connection.commit()
            return self.get_category_id(category_name)

    def delete_product(self):
        # Supprimer un produit sélectionné de la base de données
        selected_item = self.tree.selection()
        if selected_item:
            product_id = self.tree.item(selected_item, "values")[0]
            query = "DELETE FROM product WHERE id = %s"
            self.cursor.execute(query, (product_id,))
            self.connection.commit()

            # Charger à nouveau les produits dans l'interface graphique
            self.load_products()

    def update_product(self):
        # Interface graphique pour modifier un produit
        selected_item = self.tree.selection()
        if selected_item:
            update_window = tk.Toplevel(self.root)
            update_window.title("Modifier un Produit")

            # Récupérer les valeurs du produit sélectionné
            product_values = self.tree.item(selected_item, "values")

            # Afficher les valeurs actuelles
            tk.Label(update_window, text="Nom:").pack()
            name_entry = tk.Entry(update_window)
            name_entry.insert(0, product_values[1])
            name_entry.pack()

            tk.Label(update_window, text="Description:").pack()
            description_entry = tk.Entry(update_window)
            description_entry.insert(0, product_values[2])
            description_entry.pack()

            tk.Label(update_window, text="Prix:").pack()
            price_entry = tk.Entry(update_window)
            price_entry.insert(0, product_values[3])
            price_entry.pack()

            tk.Label(update_window, text="Quantité:").pack()
            quantity_entry = tk.Entry(update_window)
            quantity_entry.insert(0, product_values[4])
            quantity_entry.pack()

            tk.Label(update_window, text="Catégorie:").pack()
            category_entry = tk.Entry(update_window)
            category_entry.insert(0, product_values[5])
            category_entry.pack()

            update_button = tk.Button(update_window, text="Modifier", command=lambda: self.modify_product(
                product_values[0],
                name_entry.get(),
                description_entry.get(),
                price_entry.get(),
                quantity_entry.get(),
                category_entry.get()
            ))
            update_button.pack()

    def modify_product(self, product_id, name, description, price, quantity, category):
        # Modifier les valeurs d'un produit dans la base de données
        query = """
            UPDATE product
            SET name = %s, description = %s, price = %s, quantity = %s, id_category = %s
            WHERE id = %s
        """
        category_id = self.get_category_id(category)
        values = (name, description, price, quantity, category_id, product_id)
        self.cursor.execute(query, values)
        self.connection.commit()

        # Charger à nouveau les produits dans l'interface graphique
        self.load_products()

    def __del__(self):
        self.cursor.close()
        self.connection.close()

# Exécuter l'application
if __name__ == "__main__":
    root = tk.Tk()
    app = StockManagementApp(root)
    root.mainloop()
