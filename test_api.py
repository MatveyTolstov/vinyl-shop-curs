import requests
import json

# Тестируем API endpoints
base_url = "http://localhost:8000/api/v1"

def test_api():
    try:
        # Тест получения жанров
        print("Тестируем API...")
        
        # Тест публичного каталога товаров
        response = requests.get(f"{base_url}/products/catalog/")
        if response.status_code == 200:
            products = response.json()
            print(f"✅ Каталог товаров работает! Найдено товаров: {len(products)}")
            if products:
                print(f"   Пример товара: {products[0]['product_name']}")
        else:
            print(f"❌ Ошибка каталога: {response.status_code}")
        
        # Тест получения жанров
        response = requests.get(f"{base_url}/genres/")
        if response.status_code == 200:
            genres = response.json()
            print(f"✅ Жанры работают! Найдено жанров: {len(genres)}")
        else:
            print(f"❌ Ошибка жанров: {response.status_code}")
            
        # Тест получения исполнителей
        response = requests.get(f"{base_url}/artists/")
        if response.status_code == 200:
            artists = response.json()
            print(f"✅ Исполнители работают! Найдено исполнителей: {len(artists)}")
        else:
            print(f"❌ Ошибка исполнителей: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к серверу. Убедитесь, что сервер запущен на localhost:8000")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_api()



