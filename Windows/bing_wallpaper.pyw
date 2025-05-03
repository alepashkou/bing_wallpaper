import requests
import os
import ctypes
from datetime import datetime, timedelta
import glob

DAYS_TO_KEEP = 60  # Хранение изображений в течение 60 дней

# Очистка старых изображений
def clean_old_wallpapers(dir_path):
    try:
        # Рассчитываем пороговую дату
        threshold_date = datetime.now() - timedelta(days=DAYS_TO_KEEP)
        
        # Ищем все файлы с паттерном bing_wp_*
        files = glob.glob(os.path.join(dir_path, "bing_wp_*.jpg"))
        
        deleted_count = 0
        for file_path in files:
            # Извлекаем дату из имени файла
            file_name = os.path.basename(file_path)
            date_str = file_name.split('_')[2].split('.')[0]
            
            try:
                file_date = datetime.strptime(date_str, "%Y%m%d")
                if file_date < threshold_date:
                    os.remove(file_path)
                    deleted_count += 1
            except:
                continue  # Пропускаем файлы с некорректным именем
        
        print(f"Cleaned {deleted_count} old wallpapers")
        return True
    
    except Exception as e:
        print(f"Cleanup error: {str(e)}")
        return False

# Формируем ссылку на изображение    
def get_bing_wallpaper_url():
    try:
        api_url = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US"
        response = requests.get(api_url)
        data = response.json()
        
        if 'images' not in data or len(data['images']) == 0:
            raise Exception("No images found in Bing API response")
            
        image = data['images'][0]
        urlbase = image.get('urlbase', '')
        
        if not urlbase:
            raise Exception("URL base not found in image data")
        
        # Формируем URL для 4K изображения
        return f"https://www.bing.com{urlbase}_UHD.jpg"
    
    except Exception as e:
        raise Exception(f"Error getting Bing URL: {str(e)}")

# Скачиваем изображение в темп
def download_wallpaper(url, save_path):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return True
        return False
    except Exception as e:
        raise Exception(f"Download failed: {str(e)}")

# Устанавливаем изображение
def set_as_wallpaper(image_path):
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError("Image file not found")
            
        # Конвертируем путь в абсолютный Windows-формат
        abs_path = os.path.abspath(image_path)
        success = ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)
        
        if not success:
            raise ctypes.WinError()
        return True
    except Exception as e:
        raise Exception(f"Set wallpaper failed: {str(e)}")
    
# Главная функция
def main():
    temp_dir = os.path.join(os.environ['TEMP'], 'BingWallpapers')
    os.makedirs(temp_dir, exist_ok=True)
    

    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Updating wallpaper...")
        
        # Шаг 1: Получить URL изображения
        image_url = get_bing_wallpaper_url()
        
        # Шаг 2: Скачать изображение
        file_name = f"bing_wp_{datetime.now().strftime('%Y%m%d')}.jpg"
        save_path = os.path.join(temp_dir, file_name)
        print(save_path)
        if not download_wallpaper(image_url, save_path):
            raise Exception("Failed to download image")
        
        # Шаг 3: Установить как обои
        if not set_as_wallpaper(save_path):
            raise Exception("Failed to set wallpaper")
        
        print("Wallpaper updated successfully\n")
        
    except Exception as e:
        print(f"Error: {str(e)}\n")

# Запуск
main()