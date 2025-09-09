import json
import logging
from pathlib import Path
from tqdm import tqdm
from typing import Dict, Any
from datetime import datetime
from typing import Dict, Any, Optional

# Import from our modules
from .clean_text import clean_text
from .normalization import normalize_text, get_text_statistics

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PreprocessingPipeline:
    """Pipeline for preprocessing CV text data"""
    
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def process_single_file(self, input_path: Path) -> Optional[Dict[str, Any]]:
        """Process a single JSON file"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            raw_text = data.get('raw_text', '')
            
            # Apply preprocessing pipeline
            cleaned_text = clean_text(raw_text)
            normalized_text = normalize_text(cleaned_text)
            
            # Get statistics
            stats = get_text_statistics(cleaned_text)
            
            # Create processed data structure
            processed_data = {
                'id': data['id'],
                'raw_text': raw_text,
                'cleaned_text': cleaned_text,
                'preprocessed_text': normalized_text,
                'statistics': stats,
                'metadata': {
                    **data.get('metadata', {}),
                    'processing_timestamp': datetime.now().isoformat(),
                    'input_filename': input_path.name
                }
            }
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error processing {input_path}: {str(e)}")
            return None
    
    def save_processed_file(self, data: Dict[str, Any]):
        """Save processed data to output directory"""
        output_path = self.output_dir / f"{data['id']}_preprocessed.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def run(self):
        """Run the preprocessing pipeline on all files"""
        input_files = list(self.input_dir.glob("*.json"))
        
        if not input_files:
            logger.warning(f"No JSON files found in {self.input_dir}")
            return
        
        logger.info(f"Found {len(input_files)} files to process")
        
        success_count = 0
        for input_file in tqdm(input_files, desc="Preprocessing CVs"):
            processed_data = self.process_single_file(input_file)
            
            if processed_data:
                self.save_processed_file(processed_data)
                success_count += 1
        
        logger.info(f"Processing complete. {success_count}/{len(input_files)} files processed successfully")

def main():
    """Main function to run the preprocessing pipeline"""
    # Configuration - adjust these paths as needed
    INPUT_DIR = "../../AI_Resume_Ranker/data/processed/"  # Raw JSON files
    OUTPUT_DIR = "../../AI_Resume_Ranker/data/preprocessed/"  # Processed output
    pipeline = PreprocessingPipeline(INPUT_DIR, OUTPUT_DIR)
    pipeline.run()

if __name__ == "__main__":
    main()