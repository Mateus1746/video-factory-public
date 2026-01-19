import os
import sys
import argparse
import subprocess

def run_batch(count, query, dry_run=False):
    """Executes the auto_pipeline multiple times."""
    print("\n" + "🚀" * 20)
    print(f"🔥 INICIANDO BATCH DE {count} SIMULAÇÕES")
    if query:
        print(f"🔎 Query global: {query}")
    if dry_run:
        print("🚧 MODO DRY-RUN ATIVADO")
    print("🚀" * 20 + "\n")

    pipeline_path = os.path.join(os.path.dirname(__file__), "auto_pipeline.py")
    
    for i in range(count):
        print(f"\n[BATCH] Executando simulação {i+1} de {count}...")
        
        cmd = ["uv", "run", pipeline_path]
        if query:
            cmd.append(query)
            
        if dry_run:
            cmd.append("--dry-run")
            
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro na simulação {i+1}: {e}")
            # Continue with next iteration or stop? 
            # Usually better to continue in batch
            continue

    print("\n" + "🏁" * 20)
    print(f"✅ BATCH CONCLUÍDO: {count} execuções processadas.")
    print("🏁" * 20 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nexus V2 Batch Pipeline")
    parser.add_argument("count", type=int, help="Número de simulações para executar")
    parser.add_argument("query", nargs='?', help="Query de busca opcional")
    parser.add_argument("--dry-run", action="store_true", help="Simular sem renderizar")
    
    args = parser.parse_args()
    
    run_batch(args.count, args.query, dry_run=args.dry_run)
