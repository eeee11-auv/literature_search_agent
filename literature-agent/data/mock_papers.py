from models.paper import Paper


def get_mock_papers() -> list[Paper]:

    return [
        Paper(
            id="1",
            title="Mueller Matrix Imaging for Cancer Tissue Analysis",
            authors=["Author A", "Author B"],
            year=2024,
            doi="10.1000/test001",
            abstract=(
                "This study uses Mueller matrix imaging "
                "to analyze cancerous tissue and evaluate "
                "polarization-related diagnostic features."
            ),
            venue="Biomedical Optics",
            citation_count=20,
            relevance_score=10,
            source="mock",
        ),

        Paper(
            id="2",
            title="Polarimetric Imaging of Tumor Tissue",
            authors=["Author C"],
            year=2023,
            doi="10.1000/test002",
            abstract=(
                "Polarimetric imaging is applied to tumor "
                "tissue for pathological characterization."
            ),
            venue="Optics Journal",
            citation_count=15,
            relevance_score=8,
            source="mock",
        ),

        Paper(
            id="3",
            title="Mueller Matrix Microscopy in Pathology",
            authors=["Author D"],
            year=2022,
            doi="10.1000/test003",
            abstract=(
                "Mueller matrix microscopy is investigated "
                "for tissue pathology and cancer diagnosis."
            ),
            venue="Journal of Biomedical Optics",
            citation_count=30,
            relevance_score=9,
            source="mock",
        ),

        Paper(
            id="4",
            title="Extracellular Matrix Remodeling in Cancer",
            authors=["Author E"],
            year=2021,
            doi="10.1000/test004",
            abstract=(
                "This paper studies extracellular matrix "
                "remodeling during tumor progression."
            ),
            venue="Cancer Research",
            citation_count=100,
            relevance_score=20,
            source="mock",
        ),

        Paper(
            id="5",
            title="Deep Learning for Lung Cancer Diagnosis",
            authors=["Author F"],
            year=2024,
            doi="10.1000/test005",
            abstract=(
                "Deep learning methods are used for lung "
                "cancer diagnosis from medical images."
            ),
            venue="Medical AI",
            citation_count=40,
            relevance_score=7,
            source="mock",
        ),

        # 故意加入重复论文，测试 deduplication
        Paper(
            id="6",
            title="Mueller Matrix Imaging for Cancer Tissue Analysis",
            authors=["Author A", "Author B"],
            year=2024,
            doi="10.1000/test001",
            abstract=(
                "This study uses Mueller matrix imaging "
                "to analyze cancerous tissue."
            ),
            venue="Biomedical Optics",
            citation_count=20,
            relevance_score=10,
            source="mock",
        ),
    ]