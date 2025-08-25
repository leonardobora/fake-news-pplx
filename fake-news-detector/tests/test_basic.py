import os
import sys
import unittest
from pathlib import Path

class TestBasicFunctionality(unittest.TestCase):
    """Basic tests for the fake news detector project setup"""
    
    def test_project_structure(self):
        """Test that basic project files exist"""
        project_root = Path('.')
        
        # Check main files exist
        self.assertTrue((project_root / 'main.py').exists(), "main.py should exist")
        self.assertTrue((project_root / 'requirements.txt').exists(), "requirements.txt should exist")
        self.assertTrue((project_root / '.env.example').exists(), ".env.example should exist")
    
    def test_environment_file_template(self):
        """Test environment file template is valid"""
        env_example = Path('.env.example')
        
        if env_example.exists():
            content = env_example.read_text()
            self.assertIn('PERPLEXITY_API_KEY', content, "Should contain Perplexity API key placeholder")
            self.assertIn('OPENAI_API_KEY', content, "Should contain OpenAI API key placeholder")
    
    def test_main_py_syntax(self):
        """Test that main.py has valid Python syntax"""
        main_py = Path('main.py')
        
        if main_py.exists():
            # Try to compile the main.py file
            with open(main_py, 'r') as f:
                source = f.read()
            
            try:
                compile(source, str(main_py), 'exec')
            except SyntaxError as e:
                self.fail(f"main.py has syntax error: {e}")
    
    def test_python_environment(self):
        """Test Python environment is working"""
        # Test basic imports that should always work
        import os
        import sys
        from pathlib import Path
        
        # Test we can create and read files
        test_file = Path('test_temp.txt')
        test_content = "Hello, World!"
        
        try:
            test_file.write_text(test_content)
            read_content = test_file.read_text()
            self.assertEqual(test_content, read_content)
        finally:
            if test_file.exists():
                test_file.unlink()

if __name__ == '__main__':
    unittest.main()