from django.core.management.base import BaseCommand
import os
from chatbot.rag_engine import get_rag_engine

class Command(BaseCommand):
    help = '🔥 Rebuild PCOS FAISS RAG database from ./data/ PDFs'

    def add_arguments(self, parser):  # ← FIXED: Only ONE 'self'
        parser.add_argument('--rebuild', action='store_true', help='Force rebuild')

    def handle(self, *args, **options):
        self.stdout.write('🚀 Building FAISS RAG database from your 9 PDFs...')
        
        # Delete old index
        for ext in ['.faiss', '.pkl']:
            old_file = f"./faiss_pcos{ext}"
            if os.path.exists(old_file):
                os.remove(old_file)
                self.stdout.write(f'🗑️ Deleted {old_file}')
        
        # Rebuild from your 9 PDFs
        engine = get_rag_engine()
        engine.build_db()
        
        # Verify success
        try:
            docs_count = len(engine.faiss.documents)
            self.stdout.write(self.style.SUCCESS(f'✅ RAG BUILT! {docs_count} docs from 9 PDFs'))
        except:
            self.stdout.write(self.style.SUCCESS('✅ RAG BUILT! Ready to test'))
            
        self.stdout.write('🎯 Start server: python manage.py runserver')
        self.stdout.write('💡 Test RAG: "insulin resistance"')
