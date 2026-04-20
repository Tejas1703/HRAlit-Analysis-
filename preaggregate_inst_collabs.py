"""
Pre-aggregate institution collaboration data using ACTUAL co-authorship
from the raw HRAlit database tables.

Logic:
  1. Load publication_author → (pmid, author_id)
  2. Load author_institution → (author_id, soa_institution_id)
  3. Load institution → (soa_institution_id, institution_name, country_code)
  4. Join to get: pmid → author_id → institution_id → country_code
  5. For each publication with authors from ≥2 countries,
     generate all cross-country (inst_a, country_a, inst_b, country_b) pairs
  6. Count each pair → collab_count
  7. Keep top 20 edges per country pair; output inst_collaborations.csv
"""
import pandas as pd
import os, sys
from itertools import combinations

# ─── Paths ───────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(SCRIPT_DIR, 'Raw Data')
OUT_DIR = os.path.join(SCRIPT_DIR, 'Pre-Aggregated Data')

PA_FILE = os.path.join(RAW_DIR, 'hralit_publication_author.csv.gz')
AI_FILE = os.path.join(RAW_DIR, 'hralit_author_institution.csv.gz')
INST_FILE = os.path.join(RAW_DIR, 'hralit_institution.csv')

# ─── Config ──────────────────────────────────────────────────────────
TOP_N_EDGES_PER_PAIR = 20   # Keep top 20 institution pairs per country pair

def main():
    print("=" * 60)
    print("Co-Authorship Based Institution Collaboration Aggregation")
    print("=" * 60)
    
    # 1. Load raw tables
    print("\n[1/6] Loading publication_author...", end=" ", flush=True)
    pa = pd.read_csv(PA_FILE)
    print(f"{len(pa):,} rows  (pmid, author_id)")
    
    print("[2/6] Loading author_institution...", end=" ", flush=True)
    ai = pd.read_csv(AI_FILE)
    print(f"{len(ai):,} rows  (author_id, soa_institution_id)")
    
    print("[3/6] Loading institution...", end=" ", flush=True)
    inst = pd.read_csv(INST_FILE)[['soa_institution_id', 'institution_name', 'country_code']]
    inst = inst.dropna(subset=['country_code', 'institution_name'])
    print(f"{len(inst):,} rows  (institution_name, country_code)")
    
    # 2. Join: author_id → institution_id → country_code
    print("\n[4/6] Joining author → institution → country...", end=" ", flush=True)
    # author_institution + institution → (author_id, institution_name, country_code)
    ai_inst = ai.merge(inst, on='soa_institution_id', how='inner')
    print(f"{len(ai_inst):,} author-institution-country rows")
    
    # publication_author + ai_inst → (pmid, institution_name, country_code)
    print("       Joining with publication_author...", end=" ", flush=True)
    pub_inst = pa.merge(ai_inst[['author_id', 'institution_name', 'country_code']], on='author_id', how='inner')
    print(f"{len(pub_inst):,} publication-institution rows")
    
    # Deduplicate: for a given paper, an institution should appear only once
    pub_inst = pub_inst.drop_duplicates(subset=['pmid', 'institution_name', 'country_code'])
    print(f"       After dedup: {len(pub_inst):,} unique (pmid, institution, country) triples")
    
    # 3. For each publication, find all institutions and their countries
    print("\n[5/6] Finding cross-country institution pairs...", flush=True)
    
    # Group by pmid to get all institutions per paper
    grouped = pub_inst.groupby('pmid').apply(
        lambda g: list(zip(g['institution_name'], g['country_code']))
    ).reset_index(name='institutions')
    
    # Filter to papers with institutions from ≥2 countries
    def has_multi_country(inst_list):
        countries = set(c for _, c in inst_list)
        return len(countries) >= 2
    
    multi_country = grouped[grouped['institutions'].apply(has_multi_country)]
    print(f"       {len(multi_country):,} publications have authors from ≥2 countries (out of {len(grouped):,} total)")
    
    # 4. Generate cross-country institution pairs
    edges = []
    for _, row in multi_country.iterrows():
        insts = row['institutions']
        # Get unique (institution, country) pairs
        unique_insts = list(set(insts))
        # Generate all pairwise combinations
        for (inst_a, cc_a), (inst_b, cc_b) in combinations(unique_insts, 2):
            # Only cross-country pairs
            if cc_a != cc_b:
                # Normalize order: alphabetically by country code
                if cc_a > cc_b:
                    inst_a, cc_a, inst_b, cc_b = inst_b, cc_b, inst_a, cc_a
                edges.append((inst_a, cc_a, inst_b, cc_b))
    
    print(f"       Generated {len(edges):,} raw cross-country institution pair edges")
    
    # 5. Count and aggregate
    edge_df = pd.DataFrame(edges, columns=['inst_a', 'country_a', 'inst_b', 'country_b'])
    edge_counts = edge_df.groupby(['inst_a', 'country_a', 'inst_b', 'country_b']).size().reset_index(name='collab_count')
    edge_counts = edge_counts.sort_values('collab_count', ascending=False)
    print(f"       Unique institution pairs: {len(edge_counts):,}")
    print(f"       Total co-publications: {edge_counts['collab_count'].sum():,}")
    
    # 6. Keep top N edges per country pair to limit file size
    print(f"\n[6/6] Filtering to top {TOP_N_EDGES_PER_PAIR} edges per country pair...", end=" ", flush=True)
    
    def top_n(group):
        return group.nlargest(TOP_N_EDGES_PER_PAIR, 'collab_count')
    
    filtered = edge_counts.groupby(['country_a', 'country_b'], group_keys=False).apply(top_n)
    filtered = filtered.reset_index(drop=True)
    
    # Stats
    n_country_pairs = filtered.groupby(['country_a', 'country_b']).ngroups
    print(f"{len(filtered):,} edges across {n_country_pairs} country pairs")
    
    # Save
    out_path = os.path.join(OUT_DIR, 'inst_collaborations.csv')
    filtered.to_csv(out_path, index=False)
    file_size = os.path.getsize(out_path)
    
    print(f"\n{'=' * 60}")
    print(f"OUTPUT: {out_path}")
    print(f"SIZE:   {file_size / 1024 / 1024:.1f} MB")
    print(f"ROWS:   {len(filtered):,}")
    print(f"PAIRS:  {n_country_pairs} country pairs")
    print(f"{'=' * 60}")
    
    # Show top 10 edges
    print("\nTop 10 institution collaboration edges:")
    for _, row in filtered.head(10).iterrows():
        print(f"  {row['inst_a'][:30]:30s} ({row['country_a']}) ↔ {row['inst_b'][:30]:30s} ({row['country_b']}): {int(row['collab_count']):,}")

if __name__ == '__main__':
    main()
