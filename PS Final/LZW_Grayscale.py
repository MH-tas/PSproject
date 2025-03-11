from PIL import Image
import numpy as np

def lzw_compress(input_string):
    """LZW algoritması ile string sıkıştırma."""
    dictionary = {chr(i): i for i in range(256)}
    code = 256
    w = ""
    result = []

    for c in input_string:
        wc = w + c
        if wc in dictionary:
            w = wc
        else:
            result.append(dictionary[w])
            dictionary[wc] = code
            code += 1
            w = c

    if w:
        result.append(dictionary[w])

    return result

def lzw_decompress(compressed_data):
    """LZW algoritması ile sıkıştırılmış veriyi açma."""
    dictionary = {i: chr(i) for i in range(256)}
    code = 256
    w = chr(compressed_data[0])
    result = [w]

    for k in compressed_data[1:]:
        if k in dictionary:
            entry = dictionary[k]
        elif k == code:
            entry = w + w[0]
        else:
            raise ValueError("Hatalı sıkıştırılmış veri.")

        result.append(entry)
        dictionary[code] = w + entry[0]
        code += 1
        w = entry

    return ''.join(result)

def compress(image_path, output_file="compressed_data.txt"):
    """Görseli sıkıştırıp, sıkıştırılmış veriyi dosyaya kaydetme."""
    image = Image.open(image_path).convert("L")  # Gri tonlamaya çevir
    pixel_array = np.array(image)
    width, height = image.size

    # Piksel değerlerini string olarak birleştir
    pixel_string = ''.join(f"{pixel:03d}" for pixel in pixel_array.flatten())

    # LZW sıkıştırması uygula
    compressed_data = lzw_compress(pixel_string)
   
    # Sıkıştırılmış veriyi dosyaya kaydet
    with open(output_file, "w") as file:
        file.write(f"{width} {height}\n")  # İlk satıra genişlik ve yükseklik bilgisi ekle
        file.write(",".join(map(str, compressed_data)))  # Sıkıştırılmış veriyi virgülle kaydet

    # Dosyadaki tüm veriyi oku ve AllData'ya at
    with open(output_file, "r") as file:
        AllData = file.read()

    print(f"Sıkıştırma tamamlandı. Veriler {output_file} dosyasına kaydedildi.")
    print("AllData içeriği:", AllData[:100])  # İlk 100 karakteri yazdırarak kontrol et
    return AllData  # Sıkıştırılmış veriyi döndür

def decompress(input_file="compressed_data.txt"):
    """Dosyadan sıkıştırılmış veriyi okuyup, görüntüyü yeniden oluşturma."""
    with open(input_file, "r") as file:
        lines = file.readlines()
        width, height = map(int, lines[0].strip().split())  # İlk satırdan genişlik ve yükseklik bilgisi al
        compressed_data = list(map(int, lines[1].strip().split(",")))  # Virgülle ayrılmış sıkıştırılmış veriyi oku

    # LZW ile çözme işlemi
    decompressed_string = lzw_decompress(compressed_data)

    # Piksel değerlerini geri çevir
    try:
        decompressed_pixel_list = [int(decompressed_string[i:i + 3]) for i in range(0, len(decompressed_string), 3)]
    except ValueError:
        print("Hata: Çözülen string piksellere çevrilemedi.")
        return None

    if len(decompressed_pixel_list) != width * height:
        print(f"Hata: Piksel sayısı beklenen ({width * height}) ile eşleşmiyor.")
        return None

    # Piksel listesini yeniden matris haline getir
    decompressed_pixel_array = np.array(decompressed_pixel_list).reshape((height, width))

    # Görüntüyü oluştur ve göster
    decompressed_image = Image.fromarray(decompressed_pixel_array.astype(np.uint8))
    
    print("Görüntü başarıyla açıldı.")
    return decompressed_image

if __name__ == "__main__":

    compressed_data = compress("skypulse.bmp")  # Sıkıştırılmış veriyi al
    decompress("compressed_data.txt")  # Bu veriyi decompress fonksiyonuna ilet
