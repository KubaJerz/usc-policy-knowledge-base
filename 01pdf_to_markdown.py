from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
import os
import argparse
from tqdm import tqdm

def main(input_dir, output_dir):
    print(f"Converting PDFs from {input_dir} to Markdown in {output_dir}")
    model_dict = create_model_dict()
    converter = PdfConverter(artifact_dict=model_dict)

    for pdf_file in tqdm(os.listdir(input_dir)):
        tqdm.write(f"Processing {pdf_file}")
        if pdf_file.endswith('.pdf'):
            input_pdf_path = os.path.join(input_dir, pdf_file)
            markdown_output = converter(input_pdf_path).markdown
            output_md_path = os.path.join(output_dir, pdf_file.replace('.pdf', '.md'))
            with open(output_md_path, 'w') as md_file:
                md_file.write(markdown_output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert PDFs to Markdown format.')
    parser.add_argument('input_dir', type=str, help='Directory containing input PDF files')
    parser.add_argument('output_dir', type=str, help='Directory to save output Markdown files')
    args = parser.parse_args()

    main(args.input_dir, args.output_dir)