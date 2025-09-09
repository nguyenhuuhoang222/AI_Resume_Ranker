import os
import json
import logging
from docx import Document
from docx.opc.exceptions import PackageNotFoundError
from tqdm import tqdm
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # 3 cấp lên từ src/ingestion
RAW_FOLDER = BASE_DIR / "data/raw/docs"
PROCESSED_FOLDER = BASE_DIR / "data/processed"
ERROR_FOLDER = BASE_DIR / "data/error"  # Thư mục lưu file lỗi
BATCH_SIZE = 100
SUPPORTED_FORMATS = (".docx",)
# ===== THIẾT LẬP LOGGING =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cv_processing.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===== TẠO THƯ MỤC =====
PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)
ERROR_FOLDER.mkdir(parents=True, exist_ok=True)

def process_docx_file(file_path, error_folder):
   
    try:
        doc = Document(file_path)
        full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        
        # Kiểm tra xem file có dữ liệu không
        if not full_text.strip():
            logger.warning(f"File rỗng: {file_path.name}")
            return None
            
        return {
            "id": file_path.stem,
            "raw_text": full_text,
            "metadata": {
                "filename": file_path.name,
                "file_size": file_path.stat().st_size,
                "processing_time": None  # Sẽ được cập nhật sau
            }
        }
        
    except PackageNotFoundError:
        logger.error(f"File DOCX không hợp lệ hoặc bị hỏng: {file_path}")
        # Di chuyển file lỗi sang thư mục khác
        error_path = error_folder / file_path.name
        file_path.rename(error_path)
        return None
    except Exception as e:
        logger.error(f"Lỗi không xác định khi xử lý {file_path}: {str(e)}")
        return None

def process_batch(files, raw_folder, processed_folder, error_folder, batch_num):
   
    batch_results = []
    
    for file_path in tqdm(files, desc=f"Processing batch {batch_num}"):
        full_path = raw_folder / file_path
        json_data = process_docx_file(full_path, error_folder)
        
        if json_data:
            batch_results.append((file_path, json_data))
    
    return batch_results

def save_batch_results(batch_results, processed_folder):
 
    for filename, json_data in batch_results:
        json_filename = f"{Path(filename).stem}.json"
        json_path = processed_folder / json_filename
        
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Lỗi khi lưu file {json_path}: {str(e)}")

def main():
    logger.info(" CV processing ...")
    
    # Lấy danh sách file với đuôi mở rộng phù hợp
    all_files = [f.name for f in RAW_FOLDER.iterdir() 
                if f.is_file() and f.suffix.lower() in SUPPORTED_FORMATS]
    
    logger.info(f"Tìm thấy {len(all_files)} file để xử lý")
    
    # Xử lý theo batch
    total_batches = (len(all_files) + BATCH_SIZE - 1) // BATCH_SIZE
    
    for batch_num in range(total_batches):
        start_idx = batch_num * BATCH_SIZE
        end_idx = start_idx + BATCH_SIZE
        batch_files = all_files[start_idx:end_idx]
        
        logger.info(f"Xử lý batch {batch_num + 1}/{total_batches} ({len(batch_files)} files)")
        
        # Xử lý batch
        batch_results = process_batch(batch_files, RAW_FOLDER, PROCESSED_FOLDER, 
                                    ERROR_FOLDER, batch_num + 1)
        
        # Lưu kết quả
        save_batch_results(batch_results, PROCESSED_FOLDER)
        
        logger.info(f"Đã xử lý xong batch {batch_num + 1}, {len(batch_results)} files thành công")

    logger.info("Hoàn thành quá trình xử lý!")

# ===== ĐIỂM VÀO CHƯƠNG TRÌNH =====
if __name__ == "__main__":
    main()