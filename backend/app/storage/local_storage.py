from pathlib import Path
from app.core.config import settings
from PIL import Image
class LocalStorage:
    def __init__(self,base_directory:str):
        self.base_directory=Path(base_directory)
        self.originals_directory=(self.base_directory/"originals")
        self.transformed_directory=(self.base_directory/"transformed")
        self.originals_directory.mkdir(parents=True,exist_ok=True)
        self.transformed_directory.mkdir(parents=True,exist_ok=True)
        
    def save_original(self,filename:str,content:bytes)->str:
        filename=Path(filename)
        file_path=self.originals_directory/filename
        file_path.write_bytes(content)
        return str(file_path)
    
    def delete_file(self,file_path:str)->None:
        path=Path(file_path)
        if path.exists():
            path.unlink()      
    
    
    def save_transformed(self,
                         filename:str,
                         image:Image.Image,
                         image_format:str,
                         quality:int)->str:
        file_path=self.transformed_directory/filename
        save_kwargs={}
        
        fmt_upper=image_format.upper()
        if fmt_upper in {"JPEG","WEBP"}:
            save_kwargs["quality"]=quality
        if fmt_upper == "JPEG" and image.mode == "RGBA":
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3]) # Use alpha channel as mask
            image = background
        
        image.save(file_path,format=image_format,**save_kwargs)
        return str(file_path)
    
    
storage = LocalStorage(settings.UPLOAD_DIR)     
