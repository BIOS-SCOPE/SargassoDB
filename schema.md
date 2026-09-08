```mermaid 

erDiagram
    base {
    }
    seqBasics {
        Integer id PK
        String bottleID FK
        String sType
        String location
        String status
        String extracted
        String analyst1
    }
    seqV4_16S {
        Integer id PK
        String bottleID FK
        String cast
        String NominalDepth
        String filename
        String V4_16Sdata
    }
    seqV1V2 {
        Integer id PK
        String bottleID FK
        String cast
        String NominalDepth
        String filename
        String V1V2data
    }
    cyverse {
        Integer id PK
        String filename
        String source
        String V4_16S_found
        String V4_18S_found
        String V1V2_found
    }
    metabolites {
        Integer id PK
        String bottleID
        String dataSource
    }
    metabolitesUntargeted {
        Integer id PK
        String bottleID
        String dataSource
    }
    compositeV1V2 {
        Integer id PK
        String bottleID FK
        String cruise
        String cast
        String niskin
        String year
        String month
        String day
        String filename
    }
    NCBIunreleased {
        Integer id PK
        String biosample FK
        String sraV1V2
        String title
        String bottleID
    }
    LTTdeep {
        Integer id PK
        String sample
        String biosample FK
        String sraV1V2
        String year
        String month
        String depth
        String bottleID FK
    }
    NCBIonline {
        Integer id PK
        String contact
        String biosample FK
        String sample
        String sra
        String date
        String depth
        String lat
        String lon
        String temp
        String sal
        String fluor
        String density
        String oxy
    }
    LTTs1 {
        Integer id PK
        String biosample FK
        String sraV1V2
        String year
        String month
        String depth
        String bottleID FK
    }
    seqV4_18S {
        Integer id PK
        String bottleID FK
        String cast
        String NominalDepth
        String filename
        String V4_18Sdata
    }
    discrete {
        Integer id PK
        String bottleID
        String cruise
        String cast
        String niskin
        String yyyymmdd
        String lat
        String lon
        String depth
        String temp
        String sal
        String oxy
        String density
        String fluor
    }
    NCBIinhouse {
        Integer id PK
        String biosample
        String cruise5
        String sampleV1V2
        String sraV1V2
        String seqV1V2
        String sampleV416s
        String sraV416s
        String seqV416s
        String firstReference
        String bottleID FK
    }
    discrete ||--o{ seqBasics : "bottleID"
    discrete ||--o{ seqV4_16S : "bottleID"
    discrete ||--o{ seqV1V2 : "bottleID"
    discrete ||--o{ compositeV1V2 : "bottleID"
    discrete ||--o{ seqV4_18S : "bottleID"
    discrete ||--o{ NCBIinhouse : "bottleID"
    NCBIinhouse ||--o{ NCBIonline : "biosample"
    NCBIinhouse ||--o{ LTTs1 : "biosample"
    discrete ||--o{ LTTs1 : "bottleID"
    NCBIinhouse ||--o{ LTTdeep : "biosample"
    discrete ||--o{ LTTdeep : "bottleID"
    NCBIinhouse ||--o{ NCBIunreleased : "biosample"




```
