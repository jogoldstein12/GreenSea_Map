"""
Portfolio Analysis Module
Analyzes property portfolios for target owners
"""

import pandas as pd
import geopandas as gpd
from typing import List, Dict, Optional, Union
import logging

# Setup logging
logger = logging.getLogger(__name__)


class PortfolioAnalyzer:
    """
    Analyzes property portfolios and generates statistics for target owners.
    
    Calculates ownership metrics, financial aggregations, and geographic distributions.
    """
    
    def __init__(self):
        """Initialize portfolio analyzer."""
        self.sales_column_candidates = ["sales_amount", "sales_amou"]
        self.tax_column_candidates = ["certified_tax_total", "tax_total"]
        self.zip_column_candidates = ["par_zip", "zip", "zip_code"]
    
    def _find_column(
        self,
        df: pd.DataFrame,
        candidates: List[str],
        column_type: str = "column"
    ) -> Optional[str]:
        """
        Find first matching column from a list of candidates.
        
        Args:
            df: DataFrame to search
            candidates: List of possible column names
            column_type: Description for logging
        
        Returns:
            First matching column name, or None
        """
        for col in candidates:
            if col in df.columns:
                logger.debug(f"Found {column_type}: '{col}'")
                return col
        
        logger.warning(f"No {column_type} found. Tried: {candidates}")
        return None
    
    def filter_to_targets(
        self,
        df: Union[pd.DataFrame, gpd.GeoDataFrame],
        target_owners: List[str],
        owner_column: str = "owner_clean"
    ) -> Union[pd.DataFrame, gpd.GeoDataFrame]:
        """
        Filter DataFrame to only target owners.
        
        Args:
            df: Input DataFrame (with normalized owner column)
            target_owners: List of target owner names (should be cleaned)
            owner_column: Name of the owner column
        
        Returns:
            Filtered DataFrame containing only target owners
        
        Raises:
            ValueError: If owner column not found
        """
        if owner_column not in df.columns:
            raise ValueError(f"Owner column '{owner_column}' not found in DataFrame")
        
        if not target_owners:
            raise ValueError("Target owners list is empty")
        
        initial_count = len(df)
        filtered = df[df[owner_column].isin(target_owners)].copy()
        final_count = len(filtered)
        
        # Calculate percentage (avoid division by zero)
        percentage = (final_count/initial_count*100) if initial_count > 0 else 0.0
        
        logger.info(
            f"Filtered to target owners: {initial_count} → {final_count} properties "
            f"({percentage:.1f}%)"
        )
        
        # Log owner breakdown
        if final_count > 0:
            owner_counts = filtered[owner_column].value_counts()
            logger.info(f"Properties per owner: {owner_counts.to_dict()}")
        
        return filtered
    
    def calculate_owner_stats(
        self,
        df: pd.DataFrame,
        owner: str,
        owner_column: str = "owner_clean"
    ) -> Dict:
        """
        Calculate statistics for a single owner.
        
        Args:
            df: DataFrame with all data
            owner: Owner name to analyze
            owner_column: Name of the owner column
        
        Returns:
            Dictionary with owner statistics
        """
        # Filter to this owner
        owner_df = df[df[owner_column] == owner]
        
        if len(owner_df) == 0:
            logger.warning(f"No properties found for owner: {owner}")
            return {
                "owner": owner,
                "count": 0,
                "total_sales": 0.0,
                "total_assess": 0.0,
                "avg_sales": 0.0,
                "avg_assess": 0.0,
                "zip_table": pd.DataFrame()
            }
        
        count = len(owner_df)
        
        # Find sales column
        sales_col = self._find_column(owner_df, self.sales_column_candidates, "sales column")
        total_sales = float(owner_df[sales_col].sum()) if sales_col else 0.0
        avg_sales = (total_sales / count) if count > 0 else 0.0
        
        # Find tax assessment column
        tax_col = self._find_column(owner_df, self.tax_column_candidates, "tax column")
        total_assess = float(owner_df[tax_col].sum()) if tax_col else 0.0
        avg_assess = (total_assess / count) if count > 0 else 0.0
        
        # ZIP code breakdown
        zip_col = self._find_column(owner_df, self.zip_column_candidates, "ZIP column")
        if zip_col:
            zip_table = self._calculate_zip_breakdown(
                owner_df,
                zip_col,
                sales_col,
                tax_col
            )
        else:
            zip_table = pd.DataFrame(columns=["zip_code", "properties", "sales_total", "assess_total"])
        
        return {
            "owner": owner,
            "count": int(count),
            "total_sales": total_sales,
            "total_assess": total_assess,
            "avg_sales": avg_sales,
            "avg_assess": avg_assess,
            "zip_table": zip_table
        }
    
    def _calculate_zip_breakdown(
        self,
        df: pd.DataFrame,
        zip_col: str,
        sales_col: Optional[str],
        tax_col: Optional[str]
    ) -> pd.DataFrame:
        """
        Calculate property breakdown by ZIP code.
        
        Args:
            df: DataFrame to analyze
            zip_col: Name of ZIP code column
            sales_col: Name of sales amount column (optional)
            tax_col: Name of tax assessment column (optional)
        
        Returns:
            DataFrame with ZIP code aggregations
        """
        agg_dict = {"parcelpin": "count"}
        
        if sales_col:
            agg_dict[sales_col] = "sum"
        if tax_col:
            agg_dict[tax_col] = "sum"
        
        zip_table = (
            df.groupby(zip_col)
            .agg(agg_dict)
            .reset_index()
        )
        
        # Build new column names based on what was aggregated
        new_columns = [zip_col, "properties"]
        if sales_col:
            new_columns.append("sales_total")
        if tax_col:
            new_columns.append("assess_total")
        
        # Rename columns
        zip_table.columns = new_columns
        
        # Ensure all expected columns exist (add missing ones)
        if "sales_total" not in zip_table.columns:
            zip_table["sales_total"] = 0.0
        if "assess_total" not in zip_table.columns:
            zip_table["assess_total"] = 0.0
        
        # Sort by property count
        zip_table = zip_table.sort_values("properties", ascending=False)
        
        # Rename ZIP column to standard name
        zip_table = zip_table.rename(columns={zip_col: "zip_code"})
        
        return zip_table
    
    def calculate_all_owner_stats(
        self,
        df: pd.DataFrame,
        target_owners: List[str],
        owner_column: str = "owner_clean"
    ) -> Dict[str, Dict]:
        """
        Calculate statistics for all target owners.
        
        Args:
            df: DataFrame with property data
            target_owners: List of target owner names
            owner_column: Name of the owner column
        
        Returns:
            Dictionary mapping owner names to their statistics
        """
        logger.info(f"Calculating stats for {len(target_owners)} target owners")
        
        stats = {}
        for owner in target_owners:
            stats[owner] = self.calculate_owner_stats(df, owner, owner_column)
        
        # Log summary
        total_properties = sum(s["count"] for s in stats.values())
        logger.info(f"Total properties across all target owners: {total_properties}")
        
        return stats
    
    def calculate_aggregate_stats(
        self,
        df: pd.DataFrame,
        owner_column: str = "owner_clean"
    ) -> Dict:
        """
        Calculate aggregate statistics across all properties.
        
        Args:
            df: DataFrame with property data
            owner_column: Name of the owner column
        
        Returns:
            Dictionary with aggregate statistics
        """
        count = len(df)
        
        if count == 0:
            logger.warning("No data to aggregate")
            return {
                "count": 0,
                "unique_owners": 0,
                "total_sales": 0.0,
                "total_assess": 0.0,
                "avg_sales": 0.0,
                "avg_assess": 0.0,
                "zip_table": pd.DataFrame()
            }
        
        # Find sales column
        sales_col = self._find_column(df, self.sales_column_candidates, "sales column")
        total_sales = float(df[sales_col].sum()) if sales_col else 0.0
        avg_sales = (total_sales / count) if count > 0 else 0.0
        
        # Find tax assessment column
        tax_col = self._find_column(df, self.tax_column_candidates, "tax column")
        total_assess = float(df[tax_col].sum()) if tax_col else 0.0
        avg_assess = (total_assess / count) if count > 0 else 0.0
        
        # Unique owners
        unique_owners = int(df[owner_column].nunique())
        
        # ZIP code breakdown
        zip_col = self._find_column(df, self.zip_column_candidates, "ZIP column")
        if zip_col:
            zip_table = self._calculate_zip_breakdown(
                df,
                zip_col,
                sales_col,
                tax_col
            )
        else:
            zip_table = pd.DataFrame(columns=["zip_code", "properties", "sales_total", "assess_total"])
        
        logger.info(f"Aggregate stats: {count} properties, {unique_owners} owners")
        
        return {
            "count": int(count),
            "unique_owners": unique_owners,
            "total_sales": total_sales,
            "total_assess": total_assess,
            "avg_sales": avg_sales,
            "avg_assess": avg_assess,
            "zip_table": zip_table
        }
    
    def analyze_portfolio(
        self,
        df: pd.DataFrame,
        target_owners: List[str],
        owner_column: str = "owner_clean"
    ) -> Dict:
        """
        Complete portfolio analysis pipeline.
        
        Filters data to target owners and calculates comprehensive statistics.
        
        Args:
            df: DataFrame with property data
            target_owners: List of target owner names
            owner_column: Name of the owner column
        
        Returns:
            Dictionary with complete analysis results
        
        Example:
            >>> analyzer = PortfolioAnalyzer()
            >>> results = analyzer.analyze_portfolio(df, target_owners)
            >>> print(f"Total properties: {results['aggregate']['count']}")
        """
        logger.info("Starting portfolio analysis")
        
        # Filter to target owners
        filtered_df = self.filter_to_targets(df, target_owners, owner_column)
        
        # Calculate per-owner stats
        owner_stats = self.calculate_all_owner_stats(
            filtered_df,
            target_owners,
            owner_column
        )
        
        # Calculate aggregate stats
        aggregate_stats = self.calculate_aggregate_stats(filtered_df, owner_column)
        
        # Prepare results
        results = {
            "owner_stats": owner_stats,
            "aggregate": aggregate_stats,
            "filtered_data": filtered_df,
            "target_owner_count": len(target_owners),
            "properties_found": len(filtered_df)
        }
        
        logger.info(
            f"Portfolio analysis complete: {len(target_owners)} owners, "
            f"{len(filtered_df)} properties"
        )
        
        return results
    
    def get_summary_table(self, owner_stats: Dict[str, Dict]) -> pd.DataFrame:
        """
        Create a summary table from owner statistics.
        
        Args:
            owner_stats: Dictionary of owner statistics from analyze_portfolio
        
        Returns:
            DataFrame with owner summary
        """
        if not owner_stats:
            return pd.DataFrame()
        
        # Extract key metrics for each owner
        rows = []
        for owner, stats in owner_stats.items():
            rows.append({
                "owner": stats["owner"],
                "properties": stats["count"],
                "total_sales": stats["total_sales"],
                "avg_sales": stats["avg_sales"],
                "total_assessment": stats["total_assess"],
                "avg_assessment": stats["avg_assess"]
            })
        
        summary = pd.DataFrame(rows)
        
        # Sort by property count descending
        summary = summary.sort_values("properties", ascending=False)
        
        return summary
    
    def export_analysis(
        self,
        results: Dict,
        output_path: str
    ) -> None:
        """
        Export analysis results to Excel file.
        
        Args:
            results: Results from analyze_portfolio
            output_path: Path to output Excel file
        """
        logger.info(f"Exporting analysis to: {output_path}")
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Summary table
            summary = self.get_summary_table(results["owner_stats"])
            summary.to_excel(writer, sheet_name='Owner Summary', index=False)
            
            # Aggregate stats
            agg_df = pd.DataFrame([results["aggregate"]])
            agg_df.drop(columns=["zip_table"], errors="ignore", inplace=True)
            agg_df.to_excel(writer, sheet_name='Aggregate Stats', index=False)
            
            # Individual owner ZIP breakdowns
            for owner, stats in results["owner_stats"].items():
                if not stats["zip_table"].empty:
                    sheet_name = f"ZIP_{owner[:25]}"  # Limit sheet name length
                    stats["zip_table"].to_excel(writer, sheet_name=sheet_name, index=False)
        
        logger.info(f"Analysis exported successfully")


def analyze_target_owners(
    df: pd.DataFrame,
    target_owners: List[str],
    owner_column: str = "owner_clean"
) -> Dict:
    """
    Convenience function to analyze target owners in one call.
    
    Args:
        df: DataFrame with property data
        target_owners: List of target owner names
        owner_column: Name of the owner column
    
    Returns:
        Dictionary with analysis results
    
    Example:
        >>> results = analyze_target_owners(df, ['SMITH PROPERTIES', 'JONES LLC'])
        >>> print(f"Found {results['properties_found']} properties")
    """
    analyzer = PortfolioAnalyzer()
    return analyzer.analyze_portfolio(df, target_owners, owner_column)

