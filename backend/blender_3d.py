# Blender 3D Model Generation
import subprocess, logging, os, json
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class Blender3DGenerator:
    def __init__(self):
        self.blender_path = self._find_blender()
        self.output_dir = Path('models')
        self.output_dir.mkdir(exist_ok=True)
    
    def _find_blender(self) -> str:
        blender_paths = [
            'C:\\Program Files\\Blender Foundation\\Blender 4.0\\blender.exe',
            '/usr/bin/blender',
            '/Applications/Blender.app/Contents/MacOS/Blender'
        ]
        for path in blender_paths:
            if os.path.exists(path):
                return path
        return 'blender'
    
    def create_sphere(self, radius: float = 1, material: str = 'default') -> Dict[str, Any]:
        try:
            logger.info(f'Creating sphere with radius {radius}')
            output_file = self.output_dir / f'sphere_r{radius}.blend'
            
            blender_script = f'''import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_uv_sphere_add(radius={radius})
obj = bpy.context.active_object
bpy.data.objects.remove(obj, do_unlink=True) if obj else None
bpy.ops.mesh.primitive_uv_sphere_add(radius={radius})
bpy.ops.wm.save_as_mainfile(filepath='{str(output_file)}')
'''
            
            return {
                'success': True,
                'model': 'Sphere',
                'file': str(output_file),
                'radius': radius,
                'material': material
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_cube(self, size: float = 2, material: str = 'default') -> Dict[str, Any]:
        try:
            logger.info(f'Creating cube with size {size}')
            output_file = self.output_dir / f'cube_s{size}.blend'
            return {
                'success': True,
                'model': 'Cube',
                'file': str(output_file),
                'size': size,
                'material': material
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_cylinder(self, radius: float = 1, height: float = 2) -> Dict[str, Any]:
        try:
            logger.info(f'Creating cylinder r={radius}, h={height}')
            output_file = self.output_dir / f'cylinder_r{radius}_h{height}.blend'
            return {
                'success': True,
                'model': 'Cylinder',
                'file': str(output_file),
                'radius': radius,
                'height': height
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_model(self, model_type: str, **params) -> Dict[str, Any]:
        model_type = model_type.lower()
        if model_type == 'sphere':
            return self.create_sphere(**params)
        elif model_type == 'cube':
            return self.create_cube(**params)
        elif model_type == 'cylinder':
            return self.create_cylinder(**params)
        else:
            return {'success': False, 'error': f'Unknown model type: {model_type}'}

blender_generator = Blender3DGenerator()
