import os
from abc import ABC, abstractmethod
from typing import Dict, Union, Optional
from google import genai
from google.genai import types

# =====================================================================
# ЧАСТИНА 1: ООП-завдання (image.png)
# =====================================================================

class Product(ABC):
    """Абстрактний клас Product"""
    def __init__(self, name: str, price: float, quantity: int):
        self.name = name
        self.price = price
        self.quantity = quantity

    @abstractmethod
    def get_info(self) -> dict:
        pass


class Electronics(Product):
    """Клас Electronics, що успадковує Product"""
    def __init__(self, name: str, price: float, quantity: int, warranty_years: int):
        super().__init__(name, price, quantity)
        self.warranty_years = warranty_years

    def get_info(self) -> dict:
        return {
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "warranty_years": self.warranty_years
        }


class FoodItem(Product):
    """Клас FoodItem, що успадковує Product"""
    def __init__(self, name: str, price: float, quantity: int, expiry_days: int):
        super().__init__(name, price, quantity)
        self.expiry_days = expiry_days

    def get_info(self) -> dict:
        return {
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "expiry_days": self.expiry_days
        }


class Store:
    """Клас Store (Інкапсуляція та Поліморфізм)"""
    def __init__(self):
        # Приватний словник для інкапсуляції
        self.__inventory: Dict[str, Product] = {}

    def add_product(self, product: Product):
        # Використовуємо нижній регістр для зручності пошуку без урахування регістру
        self.__inventory[product.name.lower()] = product

    def find(self, name: str) -> Optional[Product]:
        return self.__inventory.get(name.lower(), None)

    def list_products(self) -> list:
        # Поліморфізм: викликаємо get_info() для кожного продукту, незалежно від його класу
        return [product.get_info() for product in self.__inventory.values()]


# =====================================================================
# ЧАСТИНА 2: AI-агент та Інструмент (image_2.png)
# =====================================================================

def get_product_price(product_name: str) -> dict:
    """
    Повертає інформацію про товар за його назвою.
    
    Args:
        product_name: Назва товару для пошуку в магазині.
    """
    # Створюємо об'єкт Store всередині функції згідно з ТЗ
    store = Store()
    
    # Додаємо кілька заздалегідь визначених товарів
    store.add_product(Electronics(name="Смартфон", price=25000.0, quantity=10, warranty_years=2))
    store.add_product(Electronics(name="Ноутбук", price=42000.0, quantity=5, warranty_years=1))
    store.add_product(FoodItem(name="Молоко", price=45.5, quantity=50, expiry_days=7))
    store.add_product(FoodItem(name="Хліб", price=24.0, quantity=30, expiry_days=3))
    
    # Шукаємо товар
    product = store.find(product_name)
    
    if product:
        # Поліморфне отримання даних
        return product.get_info()
    else:
        return {"available": False}


# Ініціалізація клієнта Gemini (бере API-ключ з операційної системи GEMINI_API_KEY)
client = genai.Client()

# Налаштування системного промпту агента (згідно з image_2.png)
system_instruction = (
    "Ти є консультантом інтернет-магазину. Твоє завдання — повідомляти ціни на товари, "
    "наявність та деталі (гарантія, термін придатності). "
    "Обов'язково відповідай виключно українською мовою."
)

def ask_agent(prompt_text: str):
    """Функція для відправки запиту агенту з підключеним інструментом"""
    print(f"\n🗣️ Користувач: {prompt_text}")
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt_text,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            # Передаємо нашу функцію як інструмент для моделі
            tools=[get_product_price],
            temperature=0.3
        )
    )
    print(f"🤖 Агент: {response.text}")


# =====================================================================
# ЧАСТИНА 3: Демонстрація роботи (3 запитання згідно з image_2.png)
# =====================================================================

if __name__ == "__main__":
    print("--- Запуск демонстрації AI-агента магазину ---")
    
    # Запитання 1: Про електроніку (гарантія)
    ask_agent("Підкажіть, будь ласка, яка ціна на Смартфон і яка на нього гарантія?")
    
    # Запитання 2: Про продукти харчування (термін придатності)
    ask_agent("Чи є у вас Молоко? Скільки воно коштує і який термін придатності?")
    
    # Запитання 3: Про відсутній товар
    ask_agent("Я хочу купити пральну машину. Вона є в наявності?")
