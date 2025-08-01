"""
Markdown to HTML Converter Utility
Converts Markdown text to properly formatted HTML
"""

import re


class MarkdownConverter:
    """Simple Markdown to HTML converter for travel reports."""
    
    @staticmethod
    def convert(markdown_text: str) -> str:
        """
        Convert Markdown text to HTML.
        
        Args:
            markdown_text: Raw markdown text
            
        Returns:
            Formatted HTML string
        """
        if not markdown_text:
            return ""
        
        html = markdown_text
        
        # Convert headers (both # and ** formats)
        # Convert H1 headers (# Header)
        html = re.sub(r'^#\s+(.+?)$', r'<h1 style="color: #28a745; font-size: 1.8em; margin: 25px 0 15px 0; border-bottom: 3px solid #28a745; padding-bottom: 8px;">\1</h1>', html, flags=re.MULTILINE)
        
        # Convert H2 headers (## Header)
        html = re.sub(r'^##\s+(.+?)$', r'<h2 style="color: #28a745; font-size: 1.5em; margin: 20px 0 10px 0; border-bottom: 2px solid #28a745; padding-bottom: 5px;">\1</h2>', html, flags=re.MULTILINE)
        
        # Convert H3 headers (### Header)
        html = re.sub(r'^###\s+(.+?)$', r'<h3 style="color: #333; font-size: 1.3em; margin: 15px 0 8px 0;">\1</h3>', html, flags=re.MULTILINE)
        
        # Handle any remaining ## that might not be at the start of a line
        html = re.sub(r'##\s+(.+?)(?=\n|$)', r'<strong>\1</strong>', html)
        
        # Convert old format headers (**Header**)
        html = re.sub(r'\*\*([^*]+)\*\*\s*\n\n', r'<h2 style="color: #28a745; font-size: 1.4em; margin: 20px 0 10px 0; border-bottom: 2px solid #28a745; padding-bottom: 5px;">\1</h2>\n', html)
        html = re.sub(r'\*\*([^*]+)\*\*\s*\n', r'<h3 style="color: #333; font-size: 1.2em; margin: 15px 0 8px 0;">\1</h3>\n', html)
        
        # Convert bold text (remaining **text**)
        html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)
        
        # Convert italic text
        html = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', html)
        
        # Convert bullet points
        html = re.sub(r'^\s*\*\s+(.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        
        # Wrap consecutive list items in <ul> tags
        html = re.sub(r'(<li>.*?</li>)(?:\n<li>.*?</li>)*', lambda m: '<ul style="margin: 10px 0 15px 20px;">' + m.group(0) + '</ul>', html, flags=re.DOTALL)
        
        # Convert numbered lists
        html = re.sub(r'^\s*\d+\.\s+(.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        
        # Wrap consecutive numbered list items in <ol> tags
        html = re.sub(r'(<li>.*?</li>)(?:\n<li>.*?</li>)*', lambda m: '<ol style="margin: 10px 0 15px 20px;">' + m.group(0) + '</ol>', html, flags=re.DOTALL)
        
        # Convert paragraphs (double newlines)
        paragraphs = html.split('\n\n')
        formatted_paragraphs = []
        
        for para in paragraphs:
            para = para.strip()
            if para:
                # Skip if already wrapped in HTML tags
                if not (para.startswith('<') and para.endswith('>')):
                    # Don't wrap list items or headers
                    if not (para.startswith('<ul>') or para.startswith('<ol>') or 
                           para.startswith('<h') or para.startswith('<li>')):
                        para = f'<p style="margin-bottom: 12px; text-align: justify; line-height: 1.6;">{para}</p>'
                formatted_paragraphs.append(para)
        
        html = '\n'.join(formatted_paragraphs)
        
        # Convert single newlines to <br> within paragraphs
        html = re.sub(r'(?<!>)\n(?!<)', '<br>', html)
        
        # Clean up extra spaces and newlines
        html = re.sub(r'\n\s*\n', '\n', html)
        html = re.sub(r'<br>\s*<br>', '<br>', html)
        
        return html.strip()
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean text by removing unwanted characters and formatting.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove markdown artifacts that weren't converted
        text = re.sub(r'[*_`]+', '', text)
        
        # Remove leftover # symbols at the beginning of lines
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        
        return text.strip()
