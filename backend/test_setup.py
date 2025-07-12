#!/usr/bin/env python3
"""
Script simples para testar a criação do índice FAISS
"""

import sys
import os

def main():
    print("🧪 Teste de criação do índice FAISS")
    print("=" * 50)
    
    try:
        # Importar e testar a função setup
        from api import setup_rag_system
        
        print("📦 Função setup_rag_system importada com sucesso")
        
        # Remover índice antigo se existir
        if os.path.exists("faiss_index_enhanced_"):
            import shutil
            shutil.rmtree("faiss_index_enhanced_")
            print("🗑️ Índice antigo removido")
        
        # Executar setup
        print("🏗️ Iniciando criação do índice...")
        result = setup_rag_system()
        
        if result:
            print("✅ SUCESSO: Índice FAISS criado!")
            
            # Verificar se os arquivos foram criados
            if os.path.exists("faiss_index_enhanced_/index.faiss") and os.path.exists("faiss_index_enhanced_/index.pkl"):
                print("✅ Arquivos do índice verificados")
                
                # Tentar carregar o índice
                try:
                    from api import initialize_rag_system
                    if initialize_rag_system():
                        print("✅ Índice pode ser carregado corretamente")
                    else:
                        print("❌ Erro ao carregar o índice")
                except Exception as e:
                    print(f"❌ Erro ao testar carregamento: {e}")
            else:
                print("❌ Arquivos do índice não foram criados")
        else:
            print("❌ ERRO: Falha na criação do índice")
            
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
