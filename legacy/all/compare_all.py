import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import re
import logging
from typing import Tuple, Optional, Dict, Any, List, Set, Union
import io
import warnings
import unicodedata
from difflib import SequenceMatcher
import pdfplumber
from dataclasses import dataclass
import openpyxl
from openpyxl import load_workbook
from functools import lru_cache
import hashlib


# Configuração de logging
logging.basicConfig(level=logging.WARNING)  # Reduzido para WARNING
logger = logging.getLogger(__name__)

# Suprimir avisos
warnings.filterwarnings('ignore')

@dataclass(frozen=True)
class ProcessingConfig:
    """Configurações centralizadas e otimizadas."""
    SIMILARITY_THRESHOLD_HIGH: float = 0.85
    SIMILARITY_THRESHOLD_MEDIUM: float = 0.70
    MIN_WORD_MATCHES: int = 2
    TIME_CONVERSION_TOLERANCE: float = 0.001
    MAX_HEADER_SEARCH_ROWS: int = 15  # Reduzido de 20
    MIN_DATA_ROWS: int = 1
    
    COMMON_WORDS: Set[str] = frozenset({
        'DE', 'DA', 'DO', 'DOS', 'DAS', 'E', 'EM', 'NA', 'NO', 'COM', 'PARA', 'POR'
    })
    
    COLABORADOR_PATTERNS: Set[str] = frozenset([
        'colaborador', 'nome', 'funcionario', 'empregado', 'profissional'
    ])
    
    HORAS_TRABALHADAS_PATTERNS: Set[str] = frozenset([
        'trabalhadas', 'trabalh', 'efetiva', 'executada', 'realizada'
    ])
    
    HORAS_PREVISTAS_PATTERNS: Set[str] = frozenset([
        'previstas', 'previst', 'programada', 'planejada', 'esperada'
    ])

class NameNormalizer:
    """Classe otimizada para normalização de nomes."""
    
    @staticmethod
    @lru_cache(maxsize=1000)  # Cache para evitar reprocessamento
    def normalize(nome: str) -> str:
        if not nome or pd.isna(nome):
            return ""
        
        try:
            nome = str(nome).replace('\n', ' ').replace('\r', ' ').strip()
            nome = ' '.join(nome.split())
            nome = unicodedata.normalize('NFD', nome)
            nome = ''.join(c for c in nome if unicodedata.category(c) != 'Mn')
            nome = ''.join(c for c in nome if c.isalnum() or c in {' ', '-'})
            return ' '.join(nome.split()).upper()
        except Exception:
            return str(nome).upper().strip()

class TimeConverter:
    """Classe otimizada para conversão de tempo."""
    
    @staticmethod
    @lru_cache(maxsize=500)
    def to_hours(tempo_str: Union[str, int, float]) -> float:
        """Conversão otimizada - corrigida para formato HH:MM do relatório sintético."""
        if not tempo_str or pd.isna(tempo_str):
            return 0.0
        
        try:
            if isinstance(tempo_str, (int, float)):
                return float(tempo_str)
            
            tempo_str = str(tempo_str).strip()
            
            # Trata formato HH:MM (padrão do relatório sintético)
            if ':' in tempo_str:
                negativo = tempo_str.startswith('-')
                if negativo:
                    tempo_str = tempo_str[1:]
                
                # Extrai horas e minutos (formato HH:MM ou HHH:MM)
                match = re.match(r'(\d+):(\d+)', tempo_str)
                if match:
                    horas = int(match.group(1))
                    minutos = int(match.group(2))
                    total = horas + (minutos / 60.0)
                    result = -total if negativo else total
                    print(f"Convertido '{tempo_str}' -> {result} horas")
                    return result
            
            # Fallback para formato decimal
            if not tempo_str.startswith('-'):
                tempo_str = tempo_str.replace(',', '.')
                try:
                    return float(tempo_str)
                except ValueError:
                    pass
            
            print(f"Não foi possível converter: '{tempo_str}'")
            return 0.0
            
        except Exception as e:
            print(f"Erro ao converter '{tempo_str}': {e}")
            return 0.0
    
    @staticmethod
    def to_string(horas_decimal: float) -> str:
        if pd.isna(horas_decimal):
            return "00:00"
        
        try:
            sinal = "-" if horas_decimal < 0 else ""
            horas_abs = abs(float(horas_decimal))
            horas = int(horas_abs)
            minutos = int(round((horas_abs - horas) * 60))
            
            if minutos >= 60:
                horas += minutos // 60
                minutos = minutos % 60
            
            return f"{sinal}{horas:02d}:{minutos:02d}"
        except Exception:
            return "00:00"

class OptimizedExcelProcessor:
    """Processador Excel otimizado com cache inteligente."""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.normalizer = NameNormalizer()
        self.time_converter = TimeConverter()
    
    @st.cache_data(ttl=3600)  # Cache por 1 hora
    def _get_file_hash(_self, file_content: bytes) -> str:
        """Gera hash do arquivo para cache."""
        return hashlib.md5(file_content).hexdigest()
    
    def process_synthetic_report(self, file_buffer, file_name: str = "") -> Optional[pd.DataFrame]:
        """Processador principal otimizado."""
        try:
            # Lê conteúdo uma vez
            if hasattr(file_buffer, 'read'):
                file_content = file_buffer.read()
                file_buffer = io.BytesIO(file_content)
            
            # Detecta tipo e processa
            if file_name.lower().endswith('.pdf'):
                return self._process_pdf(file_buffer)
            elif file_name.lower().endswith(('.xlsx', '.xls')):
                return self._process_excel(file_buffer, file_name)
            else:
                st.error(f"❌ Formato não suportado: {file_name}")
                return None
                
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {str(e)}")
            return None
    
    def _process_excel(self, file_buffer, file_name: str) -> Optional[pd.DataFrame]:
        """Processamento Excel simplificado e otimizado."""
        try:
            # Tenta diferentes engines automaticamente
            engines = ['openpyxl'] if file_name.endswith('.xlsx') else ['xlrd', 'openpyxl']
            df_raw = None
            
            for engine in engines:
                try:
                    if hasattr(file_buffer, 'seek'):
                        file_buffer.seek(0)
                    
                    # Lê arquivo inteiro de uma vez
                    excel_file = pd.ExcelFile(file_buffer, engine=engine)
                    
                    # Escolhe primeira planilha ou a que tem mais dados
                    sheet_name = self._select_best_sheet(excel_file)
                    df_raw = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
                    break
                    
                except Exception as e:
                    continue
            
            if df_raw is None:
                raise Exception("Nenhum engine conseguiu ler o arquivo")
            
            return self._process_excel_data(df_raw)
            
        except Exception as e:
            st.error(f"❌ Erro no processamento Excel: {str(e)}")
            return None
    
    def _select_best_sheet(self, excel_file) -> Union[str, int]:
        """Seleciona a melhor planilha baseado em heurísticas simples."""
        try:
            sheets = excel_file.sheet_names
            if len(sheets) == 1:
                return sheets[0]
            
            # Prioriza planilhas com nomes indicativos
            priority_names = ['sintético', 'sintetico', 'horas', 'colaborador', 'resumo']
            
            for sheet in sheets:
                if any(name in sheet.lower() for name in priority_names):
                    return sheet
            
            return sheets[0]  # Fallback: primeira planilha
            
        except Exception:
            return 0
    
    def _process_excel_data(self, df_raw: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Processamento otimizado dos dados Excel com debug melhorado."""
        print(f"\n=== PROCESSANDO EXCEL ===")
        print(f"Dimensões do arquivo: {len(df_raw)} linhas x {len(df_raw.columns)} colunas")
        
        # Encontra header de forma mais eficiente
        header_row = self._find_header_fast(df_raw)
        
        if header_row == -1:
            # Debug: mostra as primeiras linhas para identificar o problema
            print("=== DEBUG: PRIMEIRAS LINHAS ===")
            for i in range(min(10, len(df_raw))):
                row_preview = df_raw.iloc[i].fillna('').astype(str).tolist()[:8]  # Primeiras 8 colunas
                print(f"Linha {i+1}: {row_preview}")
            raise Exception("Header não encontrado - verifique os dados acima")
        
        # Extrai dados
        headers = df_raw.iloc[header_row].fillna('').astype(str).tolist()
        print(f"Headers identificados: {headers}")
        
        data_rows = df_raw.iloc[header_row + 1:].reset_index(drop=True)
        
        df = pd.DataFrame(data_rows.values, columns=headers)
        df = df.dropna(how='all').reset_index(drop=True)
        
        print(f"Linhas de dados após limpeza: {len(df)}")
        
        # Identifica colunas essenciais com debug
        col_colaborador = self._find_column_fast(headers, {'colaborador'})
        col_horas_trab = self._find_column_fast(headers, {'trabalhadas'})
        col_horas_prev = self._find_column_fast(headers, {'previstas'})
        
        if col_colaborador == -1:
            print("=== ERRO: Coluna colaborador não encontrada ===")
            print("Headers disponíveis:", [f"{i}: '{h}'" for i, h in enumerate(headers) if h.strip()])
            raise Exception("Coluna 'colaborador' não encontrada")
        
        if col_horas_trab == -1:
            print("=== ERRO: Coluna horas trabalhadas não encontrada ===")
            print("Headers disponíveis:", [f"{i}: '{h}'" for i, h in enumerate(headers) if h.strip()])
            raise Exception("Coluna 'trabalhadas' não encontrada")
        
        print(f"Colunas mapeadas: Colaborador={col_colaborador}, Trabalhadas={col_horas_trab}, Previstas={col_horas_prev}")
        
        # Processa dados vetorizado
        return self._extract_data_vectorized(df, col_colaborador, col_horas_trab, col_horas_prev)
    
    def _find_header_fast(self, df: pd.DataFrame) -> int:
        """Busca header otimizada - corrigida para relatório sintético."""
        # Padrões específicos para o relatório sintético
        required_patterns = {'colaborador', 'trabalhadas', 'previstas'}
        
        for idx in range(min(self.config.MAX_HEADER_SEARCH_ROWS, len(df))):
            row_text = ' '.join(df.iloc[idx].fillna('').astype(str)).lower()
            # Remove espaços extras e normaliza
            row_text = ' '.join(row_text.split())
            
            # Conta quantos padrões obrigatórios estão presentes
            matches = sum(1 for pattern in required_patterns if pattern in row_text)
            
            # Para relatório sintético, precisa ter pelo menos colaborador + uma das horas
            if matches >= 2:
                print(f"Header encontrado na linha {idx + 1}: {row_text}")
                return idx
        return -1
    
    def _find_column_fast(self, headers: List[str], patterns: Set[str]) -> int:
        """Busca coluna otimizada - corrigida para relatório sintético."""
        for i, header in enumerate(headers):
            if header and str(header).strip():  # Remove espaços extras
                header_clean = str(header).strip().lower()
                
                # Busca exata primeiro (para "trabalhadas", "previstas", etc.)
                if any(pattern == header_clean for pattern in patterns):
                    print(f"Coluna encontrada (match exato): '{header}' na posição {i}")
                    return i
                
                # Busca por substring
                if any(pattern in header_clean for pattern in patterns):
                    print(f"Coluna encontrada (substring): '{header}' na posição {i}")
                    return i
        
        print(f"Coluna não encontrada para padrões: {patterns}")
        return -1
    
    def _extract_data_vectorized(self, df: pd.DataFrame, col_colaborador: int, 
                                col_horas_trab: int, col_horas_prev: int = -1) -> pd.DataFrame:
        """Extração de dados otimizada com debug melhorado."""
        print(f"\n=== EXTRAINDO DADOS ===")
        print(f"Processando {len(df)} linhas de dados")
        
        # Filtra linhas válidas
        valid_mask = (
            df.iloc[:, col_colaborador].notna() & 
            (df.iloc[:, col_colaborador].astype(str).str.len() > 0)
        )
        df_valid = df[valid_mask].copy()
        print(f"Linhas válidas após filtro: {len(df_valid)}")
        
        # Processa nomes (vetorizado)
        df_valid['colaborador_original'] = df_valid.iloc[:, col_colaborador].astype(str).str.strip()
        
        # Remove headers repetidos
        header_patterns = ['colaborador', 'nome', 'funcionario', 'empregado', 'profissional']
        header_mask = ~df_valid['colaborador_original'].str.lower().str.contains(
            '|'.join(header_patterns), na=False
        )
        df_valid = df_valid[header_mask]
        print(f"Linhas após remover headers: {len(df_valid)}")
        
        # Remove totais
        total_mask = ~df_valid['colaborador_original'].str.lower().str.contains(
            'total|soma|subtotal', na=False
        )
        df_valid = df_valid[total_mask]
        print(f"Linhas após remover totais: {len(df_valid)}")
        
        # Normaliza nomes (aplica função em lote)
        df_valid['colaborador_limpo'] = df_valid['colaborador_original'].apply(
            self.normalizer.normalize
        )
        
        # Debug: mostra amostras dos dados originais de horas
        print(f"\n=== AMOSTRAS DE HORAS TRABALHADAS (Coluna {col_horas_trab}) ===")
        sample_horas = df_valid.iloc[:3, col_horas_trab].tolist()  # Primeiras 3 amostras
        for i, hora in enumerate(sample_horas):
            print(f"Amostra {i+1}: '{hora}' (tipo: {type(hora)})")
        
        # Converte horas (vetorizado com debug)
        print("Convertendo horas trabalhadas...")
        df_valid['horas_trabalhadas'] = df_valid.iloc[:, col_horas_trab].apply(
            self.time_converter.to_hours
        )
        
        # Mostra estatísticas das horas convertidas
        horas_convertidas = df_valid['horas_trabalhadas']
        print(f"Horas trabalhadas convertidas - Min: {horas_convertidas.min()}, Max: {horas_convertidas.max()}, Média: {horas_convertidas.mean():.2f}")
        print(f"Valores zero: {(horas_convertidas == 0).sum()}/{len(horas_convertidas)}")
        
        if col_horas_prev != -1:
            print("Convertendo horas previstas...")
            df_valid['horas_previstas'] = df_valid.iloc[:, col_horas_prev].apply(
                self.time_converter.to_hours
            )
        else:
            df_valid['horas_previstas'] = 0.0
            print("Horas previstas não encontradas, definindo como 0.0")
        
        # Remove duplicatas
        initial_count = len(df_valid)
        df_result = df_valid.drop_duplicates(subset=['colaborador_limpo'], keep='first')
        final_count = len(df_result)
        
        if initial_count != final_count:
            print(f"Duplicatas removidas: {initial_count - final_count}")
        
        # Resultado final
        result_cols = ['colaborador_original', 'colaborador_limpo', 'horas_trabalhadas', 'horas_previstas']
        df_final = df_result[result_cols].reset_index(drop=True)
        
        print(f"\n=== RESULTADO FINAL ===")
        print(f"Total de colaboradores processados: {len(df_final)}")
        print(f"Colaboradores com horas > 0: {(df_final['horas_trabalhadas'] > 0).sum()}")
        
        # Mostra primeiros 3 resultados como exemplo
        if len(df_final) > 0:
            print("\n=== PRIMEIROS 3 COLABORADORES ===")
            for i in range(min(3, len(df_final))):
                row = df_final.iloc[i]
                print(f"{i+1}. {row['colaborador_original']} -> {row['horas_trabalhadas']} horas")
        
        return df_final
    
    def _process_pdf(self, file_buffer) -> Optional[pd.DataFrame]:
        """Processamento PDF otimizado."""
        try:
            rows = self._extract_pdf_tables(file_buffer)
            if not rows:
                return None
            
            collaborators = self._find_collaborator_data_fast(rows)
            if not collaborators:
                return None
            
            df_data = []
            for collab in collaborators:
                df_data.append({
                    'colaborador_original': collab['nome'],
                    'colaborador_limpo': self.normalizer.normalize(collab['nome']),
                    'horas_trabalhadas': self.time_converter.to_hours(collab['horas_trabalhadas']),
                    'horas_previstas': 0.0
                })
            
            df_result = pd.DataFrame(df_data)
            return df_result.drop_duplicates(subset=['colaborador_limpo'], keep='first')
            
        except Exception as e:
            st.error(f"❌ Erro no PDF: {str(e)}")
            return None
    
    def _extract_pdf_tables(self, file_buffer) -> List[List[str]]:
        """Extração otimizada de tabelas PDF."""
        all_rows = []
        try:
            with pdfplumber.open(file_buffer) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            all_rows.extend([
                                [str(cell).strip() if cell else "" for cell in row]
                                for row in table if row and any(cell for cell in row if cell)
                            ])
            return all_rows
        except Exception:
            return []
    
    def _find_collaborator_data_fast(self, rows: List[List[str]]) -> List[Dict[str, str]]:
        """Identificação rápida de colaboradores."""
        collaborators = []
        time_pattern = re.compile(r'^\d{1,3}:\d{2}$')
        
        for row in rows:
            if len(row) < 3:
                continue
            
            row_text = ' '.join(row).lower()
            if any(word in row_text for word in ['colaborador', 'total', 'previstas']):
                continue
            
            # Encontra nome e horas
            nome = None
            horas = None
            
            for cell in row:
                if cell and time_pattern.match(cell.strip()):
                    horas = cell.strip()
                elif cell and len(cell.split()) >= 2 and not cell.isdigit():
                    nome = cell.strip()
            
            if nome and horas:
                collaborators.append({'nome': nome, 'horas_trabalhadas': horas})
        
        return collaborators

class OptimizedAnalyzer:
    """Analisador principal otimizado."""
    
    def __init__(self):
        self.config = ProcessingConfig()
        self.excel_processor = OptimizedExcelProcessor(self.config)
        self.normalizer = NameNormalizer()
        self.time_converter = TimeConverter()
        
    def process_faturamento(self, arquivos) -> Optional[pd.DataFrame]:
        """Processa faturamento de forma otimizada."""
        if not arquivos:
            return None
        
        all_data = []
        
        for arquivo in arquivos:
            try:
                df = pd.read_excel(arquivo, header=None)
                
                # Busca header rapidamente
                header_row = self._find_faturamento_header(df)
                if header_row == -1:
                    continue
                
                headers = df.iloc[header_row].fillna('').astype(str).tolist()
                data = df.iloc[header_row + 1:].reset_index(drop=True)
                data.columns = headers
                
                # Identifica colunas
                col_prof = self._find_prof_column(headers)
                col_horas = self._find_horas_column(headers)
                
                if col_prof != -1 and col_horas != -1:
                    # Processa dados
                    valid_data = data[(data.iloc[:, col_prof].notna()) & 
                                    (data.iloc[:, col_prof].astype(str).str.len() > 2)]
                    
                    for _, row in valid_data.iterrows():
                        prof = str(row.iloc[col_prof]).strip()
                        horas = self.time_converter.to_hours(row.iloc[col_horas])
                        
                        if prof and not any(word in prof.lower() for word in ['profissional', 'total']):
                            all_data.append({
                                'profissional_original': prof,
                                'profissional_limpo': self.normalizer.normalize(prof),
                                'horas_apropriadas': horas,
                                'is_faturado': True
                            })
            
            except Exception as e:
                st.warning(f"⚠️ Erro no arquivo {arquivo.name}: {str(e)}")
                continue
        
        if not all_data:
            return None
        
        # Agrupa por profissional
        df_all = pd.DataFrame(all_data)
        df_grouped = df_all.groupby('profissional_limpo').agg({
            'profissional_original': 'first',
            'horas_apropriadas': 'sum',
            'is_faturado': 'any'
        }).reset_index()
        
        return df_grouped
    
    def _find_faturamento_header(self, df: pd.DataFrame) -> int:
        """Busca header no faturamento."""
        for i in range(min(10, len(df))):
            row_text = ' '.join(df.iloc[i].fillna('').astype(str)).lower()
            if 'profissional' in row_text and ('quant' in row_text or 'hora' in row_text):
                return i
        return -1
    
    def _find_prof_column(self, headers: List[str]) -> int:
        """Encontra coluna de profissional."""
        for i, header in enumerate(headers):
            if 'profissional' in str(header).lower():
                return i
        return -1
    
    def _find_horas_column(self, headers: List[str]) -> int:
        """Encontra coluna de horas."""
        for i, header in enumerate(headers):
            if any(word in str(header).lower() for word in ['quant', 'hora']):
                return i
        return -1
    
    def compare_reports(self, df_sintetico: pd.DataFrame, df_faturamento: pd.DataFrame) -> pd.DataFrame:
        """Comparação otimizada de relatórios."""
        # Merge inicial
        df_merged = df_sintetico.merge(
            df_faturamento,
            left_on='colaborador_limpo',
            right_on='profissional_limpo',
            how='left'
        )
        
        # Preenche valores faltantes
        df_merged['horas_apropriadas'] = df_merged['horas_apropriadas'].fillna(0.0)
        df_merged['is_faturado'] = df_merged['is_faturado'].fillna(False)
        
        # Calcula diferenças vetorizado
        df_merged['diferenca_horas'] = (
            df_merged['horas_trabalhadas'] - df_merged['horas_apropriadas']
        )
        df_merged['diferenca_absoluta'] = df_merged['diferenca_horas'].abs()
        
        # Categoriza
        conditions = [
            df_merged['diferenca_absoluta'] < self.config.TIME_CONVERSION_TOLERANCE,
            df_merged['diferenca_horas'] > 0,
            df_merged['diferenca_horas'] < 0
        ]
        choices = ['✅ Aprovado', '⬆️ Mais trabalhadas', '⬇️ Menos trabalhadas']
        df_merged['categoria_diferenca'] = np.select(conditions, choices, default='❓ Indefinido')
        
        # Status
        def get_status(row):
            if not row['is_faturado']:
                return '🔍 Não encontrado'
            elif row['diferenca_absoluta'] < self.config.TIME_CONVERSION_TOLERANCE:
                return '✅ Aprovado'
            else:
                return '❌ Divergente'
        
        df_merged['status'] = df_merged.apply(get_status, axis=1)
        
        return df_merged

def generate_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """Gera estatísticas otimizada."""
    if df is None or len(df) == 0:
        return {}
    
    total = len(df)
    faturados = df['is_faturado'].sum()
    aprovados = (df['diferenca_absoluta'] < ProcessingConfig.TIME_CONVERSION_TOLERANCE).sum()
    
    return {
        'total_colaboradores': total,
        'colaboradores_faturados': int(faturados),
        'colaboradores_nao_faturados': int(total - faturados),
        'colaboradores_aprovados': int(aprovados),
        'colaboradores_divergentes': int(total - aprovados),
        'total_horas_trabalhadas': df['horas_trabalhadas'].sum(),
        'total_horas_apropriadas': df['horas_apropriadas'].sum(),
        'diferenca_total': df['diferenca_horas'].sum(),
        'percentual_aprovados': (aprovados / total * 100) if total > 0 else 0
    }

def main():

    
    # Inicializa analyzer no session_state
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = OptimizedAnalyzer()
        st.session_state.df_sintetico = None
        st.session_state.df_faturamento = None
    
    # Layout principal
    col1, col2 = st.columns([1, 1])
    
    # Processamento Sintético
    with col1:
        st.subheader("🏢 Relatório Sintético")
        # Upload sintético
        arquivo_sintetico = st.file_uploader(
            "📊 Relatório Sintético",
            type=['pdf', 'xlsx', 'xls'],
            help="PDF ou Excel com colaboradores e horas trabalhadas"
        )
        
        if arquivo_sintetico:
            if st.session_state.df_sintetico is None:
                with st.spinner("Processando..."):
                    # Captura o output do processamento para debug
                    import sys
                    from io import StringIO
                    
                    # Redireciona prints para capturar logs
                    old_stdout = sys.stdout
                    log_capture = StringIO()
                    sys.stdout = log_capture
                    
                    try:
                        df = st.session_state.analyzer.excel_processor.process_synthetic_report(
                            arquivo_sintetico, arquivo_sintetico.name
                        )
                        
                        # Restaura stdout
                        sys.stdout = old_stdout
                        log_output = log_capture.getvalue()
                        
                        if df is not None:
                            st.session_state.df_sintetico = df
                            st.success(f"✅ {len(df)} colaboradores processados")
                            
                            # Mostra logs de processamento em expander
                            if log_output.strip():
                                with st.expander("🔍 Log de Processamento"):
                                    st.text(log_output)
                            
                            with st.expander("👀 Preview dos Dados"):
                                preview_df = df[['colaborador_original', 'horas_trabalhadas']].head()
                                # Formata as horas para melhor visualização
                                preview_df['horas_trabalhadas_formatadas'] = preview_df['horas_trabalhadas'].apply(
                                    lambda x: TimeConverter.to_string(x)
                                )
                                st.dataframe(preview_df[['colaborador_original', 'horas_trabalhadas_formatadas']])
                        else:
                            # Restaura stdout mesmo em caso de erro
                            sys.stdout = old_stdout
                            log_output = log_capture.getvalue()
                            
                            if log_output.strip():
                                st.error("❌ Erro no processamento. Veja os detalhes abaixo:")
                                with st.expander("🔍 Detalhes do Erro", expanded=True):
                                    st.text(log_output)
                    
                    except Exception as e:
                        # Garante que stdout seja restaurado
                        sys.stdout = old_stdout
                        log_output = log_capture.getvalue()
                        
                        st.error(f"❌ Erro: {str(e)}")
                        if log_output.strip():
                            with st.expander("🔍 Log de Debug", expanded=True):
                                st.text(log_output)
            else:
                st.success(f"✅ {len(st.session_state.df_sintetico)} colaboradores carregados")
                
                # Mostra resumo dos dados carregados
                df = st.session_state.df_sintetico
                horas_total = df['horas_trabalhadas'].sum()
                horas_media = df['horas_trabalhadas'].mean()
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Total de Horas", TimeConverter.to_string(horas_total))
                with col_b:
                    st.metric("Média por Colaborador", TimeConverter.to_string(horas_media))
        else:
            st.info("📤 Aguardando upload...")
    
    # Processamento Faturamento
    with col2:
        st.subheader("💰 Relatório Faturamento")
        # Upload faturamento
        arquivos_faturamento = st.file_uploader(
            "💰 Relatório(s) Faturamento",
            type=['xlsx', 'xls'],
            accept_multiple_files=True,
            help="Excel com profissionais e horas apropriadas"
        )
        
        if arquivos_faturamento:
            if st.session_state.df_faturamento is None:
                with st.spinner("Processando..."):
                    df = st.session_state.analyzer.process_faturamento(arquivos_faturamento)
                    
                    if df is not None:
                        st.session_state.df_faturamento = df
                        st.success(f"✅ {len(df)} profissionais processados")
                        
                        with st.expander("👀 Preview"):
                            st.dataframe(df[['profissional_original', 'horas_apropriadas']].head())
            else:
                st.success(f"✅ {len(st.session_state.df_faturamento)} profissionais carregados")
        else:
            st.info("📤 Aguardando upload...")
    
    # Análise Comparativa
    if st.session_state.df_sintetico is not None and st.session_state.df_faturamento is not None:
        st.header("🔍 Análise Comparativa")
        
        if st.button("🚀 Gerar Análise", type="primary"):
            with st.spinner("Analisando..."):
                df_comparacao = st.session_state.analyzer.compare_reports(
                    st.session_state.df_sintetico,
                    st.session_state.df_faturamento
                )
                
                # Estatísticas
                stats = generate_statistics(df_comparacao)
                
                st.subheader("📈 Resumo Executivo")
                
                # Métricas principais
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("👥 Total", stats['total_colaboradores'])
                
                with col2:
                    st.metric("✅ Aprovados", stats['colaboradores_aprovados'])
                
                with col3:
                    st.metric("❌ Divergentes", stats['colaboradores_divergentes'])
                
                with col4:
                    perc = stats['percentual_aprovados']
                    st.metric("📊 % Aprovação", f"{perc:.1f}%")
                
                # Status colorido
                if perc >= 90:
                    st.success(f"🎯 Excelente! {perc:.1f}% dos colaboradores aprovados")
                elif perc >= 70:
                    st.warning(f"⚠️ Regular: {perc:.1f}% dos colaboradores aprovados")
                else:
                    st.error(f"❌ Crítico: apenas {perc:.1f}% aprovados")
                
                # Tabela de resumo detalhada - AQUI ESTÁ A PARTE QUE ESTAVA FALTANDO
                st.subheader("📋 Tabela de Resultados")
                
                # Filtros
                col_filter1, col_filter2 = st.columns(2)
                
                with col_filter1:
                    status_filter = st.selectbox(
                        "Filtrar por Status:",
                        ['Todos'] + df_comparacao['status'].unique().tolist()
                    )
                
                with col_filter2:
                    categoria_filter = st.selectbox(
                        "Filtrar por Categoria:",
                        ['Todas'] + df_comparacao['categoria_diferenca'].unique().tolist()
                    )
                
                # Aplica filtros
                df_filtered = df_comparacao.copy()
                
                if status_filter != 'Todos':
                    df_filtered = df_filtered[df_filtered['status'] == status_filter]
                
                if categoria_filter != 'Todas':
                    df_filtered = df_filtered[df_filtered['categoria_diferenca'] == categoria_filter]
                
                # Prepara dados para exibição
                df_display = df_filtered[[
                    'colaborador_original', 'horas_trabalhadas', 'horas_apropriadas',
                    'diferenca_horas', 'categoria_diferenca', 'status'
                ]].copy()
                
                # Formata horas para exibição
                df_display['horas_trabalhadas'] = df_display['horas_trabalhadas'].apply(
                    lambda x: TimeConverter.to_string(x)
                )
                df_display['horas_apropriadas'] = df_display['horas_apropriadas'].apply(
                    lambda x: TimeConverter.to_string(x)
                )
                df_display['diferenca_horas'] = df_display['diferenca_horas'].apply(
                    lambda x: TimeConverter.to_string(x)
                )
                
                # Renomeia colunas
                df_display.columns = [
                    'Colaborador', 'Horas Trabalhadas', 'Horas Apropriadas',
                    'Diferença', 'Categoria', 'Status'
                ]
                
                # Exibe tabela
                st.dataframe(
                    df_display,
                    use_container_width=True,
                    height=400
                )
                
                # Resumo do filtro
                st.info(f"📊 Exibindo {len(df_filtered)} de {len(df_comparacao)} colaboradores")
                
                # Botão de download
                csv = df_display.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 Baixar Resultados (CSV)",
                    data=csv,
                    file_name=f"analise_relatorios_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
    
    # Reset button
    # if st.sidebar.button("🔄 Limpar Dados", type="secondary"):
    #     st.session_state.df_sintetico = None
    #     st.session_state.df_faturamento = None
    #     st.rerun()

if __name__ == "__main__":
    main()