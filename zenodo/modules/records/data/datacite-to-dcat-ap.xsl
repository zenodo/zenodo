<?xml version="1.0" encoding="UTF-8"?>

<!--  

  Copyright 2015-2019 EUROPEAN UNION
  Licensed under the EUPL, Version 1.1 or - as soon they will be approved by
  the European Commission - subsequent versions of the EUPL (the "Licence");
  You may not use this work except in compliance with the Licence.
  You may obtain a copy of the Licence at:
 
  http://ec.europa.eu/idabc/eupl
 
  Unless required by applicable law or agreed to in writing, software
  distributed under the Licence is distributed on an "AS IS" basis,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the Licence for the specific language governing permissions and
  limitations under the Licence.
 
  Authors: European Commission, Joint Research Centre (JRC)
           Andrea Perego <andrea.perego@ec.europa.eu>
 
-->

<!--

  PURPOSE AND USAGE

  This XSLT is a proof of concept for the implementation of the specification
  concerning the DataCite profile of DCAT-AP (CiteDCAT-AP)
    
  As such, this XSLT must be considered as unstable, and can be updated any 
  time based on the revisions to the CiteDCAT-AP specifications.  
-->

<xsl:transform
    xmlns:adms   = "http://www.w3.org/ns/adms#"
    xmlns:cnt    = "http://www.w3.org/2011/content#"
    xmlns:dc     = "http://purl.org/dc/elements/1.1/" 
    xmlns:dct    = "http://purl.org/dc/terms/"
    xmlns:dctype = "http://purl.org/dc/dcmitype/"
    xmlns:dcat   = "http://www.w3.org/ns/dcat#"
    xmlns:dtct2.2 = "http://datacite.org/schema/kernel-2.2"
    xmlns:dtct3  = "http://datacite.org/schema/kernel-3"
    xmlns:dtct4  = "http://datacite.org/schema/kernel-4"
    xmlns:duv    = "http://www.w3.org/ns/duv#"
    xmlns:earl   = "http://www.w3.org/ns/earl#"
    xmlns:foaf   = "http://xmlns.com/foaf/0.1/"
    xmlns:frapo  = "http://purl.org/cerif/frapo/"
    xmlns:geo    = "http://www.w3.org/2003/01/geo/wgs84_pos#"
    xmlns:gsp    = "http://www.opengis.net/ont/geosparql#"
    xmlns:locn   = "http://www.w3.org/ns/locn#"
    xmlns:oa     = "http://www.w3.org/ns/oa#"
    xmlns:org    = "http://www.w3.org/ns/org#"
    xmlns:owl    = "http://www.w3.org/2002/07/owl#"
    xmlns:prov   = "http://www.w3.org/ns/prov#"
    xmlns:rdf    = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:rdfs   = "http://www.w3.org/2000/01/rdf-schema#"
    xmlns:schema = "http://schema.org/"
    xmlns:skos   = "http://www.w3.org/2004/02/skos/core#"
    xmlns:vcard  = "http://www.w3.org/2006/vcard/ns#"
    xmlns:xlink  = "http://www.w3.org/1999/xlink" 
    xmlns:xsi    = "http://www.w3.org/2001/XMLSchema-instance" 
    xmlns:xsl    = "http://www.w3.org/1999/XSL/Transform"
    xmlns:wdrs   = "http://www.w3.org/2007/05/powder-s#"
    exclude-result-prefixes = "cnt dtct2.2 dtct3 dtct4 earl oa xlink xsi xsl"
    version="1.0">

  <xsl:output method="xml"
              indent="yes"
              encoding="utf-8"
              cdata-section-elements="locn:geometry" />

<!-- Vars used when transforming strings into upper/lowercase. -->

    <xsl:variable name="lowercase" select="'abcdefghijklmnopqrstuvwxyz'"/>
    <xsl:variable name="uppercase" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'"/>
    
<!-- The namespace of the DataCite metadata schema changes depending on the schema version -->
<!--
    <xsl:param name="dtctNsUriPrefix">http://datacite.org/schema/kernel-</xsl:param>
-->
<!--

  Mapping parameters
  ==================
  
  This section includes mapping parameters to be modified manually. 

-->

<!-- Parameter $profile -->
<!--

  This parameter specifies the CiteDCAT-AP profile to be used:
  - value "core": the CiteDCAT-AP Core profile, which includes only the DataCite metadata elements supported in DCAT-AP
  - value "extended": the CiteDCAT-AP Extended profile, which defines mappings for all the DataCite metadata elements
  
  The current specifications for the core and extended CiteDCAT-AP profiles are available on the JRC GitHub repository:

    https://github.com/ec-jrc/datacite-to-dcat-ap/

-->

<!-- Uncomment to use CiteDCAT-AP Core -->
<!--
  <xsl:param name="profile">core</xsl:param>
-->
<!-- Uncomment to use CiteDCAT-AP Extended -->
  <xsl:param name="profile">extended</xsl:param>

<!--

  Other global parameters
  =======================
  
-->
  
<!-- URI and URN of the spatial reference system (SRS) used in the bounding box.
     The default SRS is CRS84. If a different SRS is used, also parameter 
     $SrsAxisOrder must be specified. -->

<!-- Old param
  <xsl:param name="srid">4326</xsl:param>
-->
<!-- The SRS URI is used in the WKT and GML encodings of the bounding box. -->
  <xsl:param name="SrsUri">http://www.opengis.net/def/crs/OGC/1.3/CRS84</xsl:param>
<!-- The SRS URN is used in the GeoJSON encoding of the bounding box. -->
  <xsl:param name="SrsUrn">urn:ogc:def:crs:OGC:1.3:CRS84</xsl:param>

<!-- Axis order for the reference SRS: 
     - "LonLat": longitude / latitude
     - "LatLon": latitude / longitude.
     The axis order must be specified only if the reference SRS is different from CRS84. 
     If the reference SRS is CRS84, this parameter is ignored. -->
  
  <xsl:param name="SrsAxisOrder">LonLat</xsl:param>

<!-- Namespaces -->

  <xsl:param name="xsd">http://www.w3.org/2001/XMLSchema#</xsl:param>
  <xsl:param name="dct">http://purl.org/dc/terms/</xsl:param>
  <xsl:param name="dctype">http://purl.org/dc/dcmitype/</xsl:param>
  <xsl:param name="foaf">http://xmlns.com/foaf/0.1/</xsl:param>
  <xsl:param name="vcard">http://www.w3.org/2006/vcard/ns#</xsl:param>
<!-- Currently not used.
  <xsl:param name="timeUri">http://placetime.com/</xsl:param>
  <xsl:param name="timeInstantUri" select="concat($timeUri,'instant/gregorian/')"/>
  <xsl:param name="timeIntervalUri" select="concat($timeUri,'interval/gregorian/')"/>
-->
  <xsl:param name="dcat">http://www.w3.org/ns/dcat#</xsl:param>
  <xsl:param name="gsp">http://www.opengis.net/ont/geosparql#</xsl:param>

<!-- MDR NALs and other code lists -->

  <xsl:param name="op">http://publications.europa.eu/resource/authority/</xsl:param>
  <xsl:param name="oplang" select="concat($op,'language/')"/>
  <xsl:param name="opcb" select="concat($op,'corporate-body/')"/>
  <xsl:param name="oplic" select="concat($op,'licence/')"/>
  <xsl:param name="opar" select="concat($op,'access-right/')"/>
  <xsl:param name="opds" select="concat($op,'dataset-status/')"/>
<!--  
  <xsl:param name="opcountry" select="concat($op,'country/')"/>
  <xsl:param name="opfq" select="concat($op,'frequency/')"/>
  <xsl:param name="cldFrequency">http://purl.org/cld/freq/</xsl:param>
-->
  <xsl:param name="ianaMT">https://www.iana.org/assignments/media-types/</xsl:param>
<!-- This is used as the datatype for the GeoJSON-based encoding of the bounding box. -->
  <xsl:param name="geojsonMediaTypeUri">https://www.iana.org/assignments/media-types/application/vnd.geo+json</xsl:param>

<!-- INSPIRE code list URIs -->
<!--  
  <xsl:param name="INSPIRECodelistUri">http://inspire.ec.europa.eu/metadata-codelist/</xsl:param>
  <xsl:param name="SpatialDataServiceCategoryCodelistUri" select="concat($INSPIRECodelistUri,'SpatialDataServiceCategory')"/>
  <xsl:param name="DegreeOfConformityCodelistUri" select="concat($INSPIRECodelistUri,'DegreeOfConformity')"/>
  <xsl:param name="ResourceTypeCodelistUri" select="concat($INSPIRECodelistUri,'ResourceType')"/>
  <xsl:param name="ResponsiblePartyRoleCodelistUri" select="concat($INSPIRECodelistUri,'ResponsiblePartyRole')"/>
  <xsl:param name="SpatialDataServiceTypeCodelistUri" select="concat($INSPIRECodelistUri,'SpatialDataServiceType')"/>
  <xsl:param name="TopicCategoryCodelistUri" select="concat($INSPIRECodelistUri,'TopicCategory')"/>
-->
<!-- INSPIRE code list URIs (not yet supported; the URI pattern is tentative) -->
<!--  
  <xsl:param name="SpatialRepresentationTypeCodelistUri" select="concat($INSPIRECodelistUri,'SpatialRepresentationTypeCode')"/>
  <xsl:param name="MaintenanceFrequencyCodelistUri" select="concat($INSPIRECodelistUri,'MaintenanceFrequencyCode')"/>
-->
<!-- 

  Master template     
  ===============
 
 -->
 
  <xsl:template match="/">
    <rdf:RDF>
      <xsl:apply-templates select="*[local-name() = 'resource' and starts-with(namespace-uri(), 'http://datacite.org/schema/kernel-')]|//*[local-name() = 'resource' and starts-with(namespace-uri(), 'http://datacite.org/schema/kernel-')]"/>
    </rdf:RDF>
  </xsl:template>

<!-- 

  Metadata template     
  =================
 
 -->
 
  <xsl:template match="*[local-name() = 'resource' and starts-with(namespace-uri(), 'http://datacite.org/schema/kernel-')]|//*[local-name() = 'resource' and starts-with(namespace-uri(), 'http://datacite.org/schema/kernel-')]">
<!-- 

  Parameters to create HTTP URIs for the resource and the corresponding metadata record
  _____________________________________________________________________________________

  These parameters must be customised depending on the strategy used to assign HTTP URIs.
  
  The default rule implies that HTTP URIs are specified for the metadata file identifier
  (metadata URI) and the resource identifier (resource URI).

-->

    <xsl:param name="ResourceUri">
      <xsl:variable name="identifier" select="normalize-space(*[local-name() = 'identifier'])"/>
      <xsl:variable name="type" select="normalize-space(translate(*[local-name() = 'identifier']/@identifierType,$uppercase,$lowercase))"/>
      <xsl:variable name="schemeURI" select="*[local-name() = 'identifier']/@schemeURI"/>
      <xsl:variable name="uri">
        <xsl:call-template name="IdentifierURI">
          <xsl:with-param name="identifier" select="$identifier"/>
          <xsl:with-param name="type" select="$type"/>
          <xsl:with-param name="schemeURI" select="$schemeURI"/>
        </xsl:call-template>
      </xsl:variable>    
      <xsl:variable name="urilc" select="translate($uri,$uppercase,$lowercase)"/>
      <xsl:if test="$uri != '' and ( starts-with($urilc, 'http://') or starts-with($urilc, 'https://') )">
        <xsl:value-of select="$uri"/>
      </xsl:if>
    </xsl:param>

    <xsl:param name="MetadataUri"/>
  
<!-- 

  Other parameters
  ________________
  
-->
  
<!-- Resource type -->

    <xsl:param name="ResourceType">
      <xsl:variable name="type" select="normalize-space(translate(*[local-name() = 'resourceType']/@resourceTypeGeneral,$uppercase,$lowercase))"/>
      <xsl:choose>
        <xsl:when test="$type = 'audiovisual'">dataset</xsl:when>
        <xsl:when test="$type = 'collection'">dataset</xsl:when>
<!-- Added in DataCite v4.1 -->
        <xsl:when test="$type = 'datapaper'">dataset</xsl:when>
        <xsl:when test="$type = 'dataset'">dataset</xsl:when>
        <xsl:when test="$type = 'event'">event</xsl:when>
        <xsl:when test="$type = 'image'">dataset</xsl:when>
        <xsl:when test="$type = 'interactiveresource'">dataset</xsl:when>
        <xsl:when test="$type = 'model'">dataset</xsl:when>
        <xsl:when test="$type = 'physicalobject'">physicalobject</xsl:when>
        <xsl:when test="$type = 'service'">service</xsl:when>
        <xsl:when test="$type = 'software'">dataset</xsl:when>
        <xsl:when test="$type = 'sound'">dataset</xsl:when>
        <xsl:when test="$type = 'text'">dataset</xsl:when>
        <xsl:when test="$type = 'workflow'">dataset</xsl:when>
        <xsl:when test="$type = 'other'">other</xsl:when>
        <xsl:otherwise>other</xsl:otherwise>
      </xsl:choose>
    </xsl:param>
    
<!-- Metadata description (metadata on metadata) -->

    <xsl:param name="MetadataDescription"/>
    
<!-- Resource description (resource metadata) -->

    <xsl:param name="ResourceDescription">

<!-- Resource type -->
      <xsl:apply-templates select="*[local-name() = 'resourceType']"/>
<!-- Identifier -->
      <xsl:apply-templates select="*[local-name() = 'identifier']">
        <xsl:with-param name="ResourceType" select="$ResourceType"/>
      </xsl:apply-templates>
<!-- Creators -->
      <xsl:apply-templates select="*[local-name() = 'creators']/*[local-name() = 'creator']"/>
<!-- Titles -->
      <xsl:apply-templates select="*[local-name() = 'titles']/*[local-name() = 'title']"/>
<!-- Publisher -->
      <xsl:apply-templates select="*[local-name() = 'publisher']"/>
<!-- Publication year-->
      <xsl:apply-templates select="*[local-name() = 'publicationYear']"/>
<!-- Subjects -->
      <xsl:apply-templates select="*[local-name() = 'subjects']/*[local-name() = 'subject']"/>
<!-- Funding references -->
      
      <xsl:if test="$profile = 'extended'">
        <xsl:for-each select="*[local-name() = 'fundingReferences']/*[local-name() = 'fundingReference']">
          <xsl:call-template name="FundingReferences"/>
        </xsl:for-each>
      </xsl:if>
        
<!-- Contributors-->
      <xsl:apply-templates select="*[local-name() = 'contributors']/*[local-name() = 'contributor']"/>
<!-- Dates -->
      <xsl:apply-templates select="*[local-name() = 'dates']/*[local-name() = 'date']"/>
<!-- Language -->
      <xsl:apply-templates select="*[local-name() = 'language']"/>
<!-- Alternate identifiers-->
      <xsl:apply-templates select="*[local-name() = 'alternateIdentifiers']/*[local-name() = 'alternateIdentifier']"/>
<!-- Related identifiers -->
      <xsl:apply-templates select="*[local-name() = 'relatedIdentifiers']/*[local-name() = 'relatedIdentifier']"/>
<!-- Version -->
      <xsl:apply-templates select="*[local-name() = 'version']"/>
<!-- Descriptions -->
      <xsl:apply-templates select="*[local-name() = 'descriptions']/*[local-name() = 'description']"/>
<!-- Geo locations -->
      <xsl:apply-templates select="*[local-name() = 'geoLocations']/*[local-name() = 'geoLocation']"/>
<!-- Access rights -->
<!-- For DataCite schema version < 3 -->
      <xsl:apply-templates select="*[local-name() = 'rights']">
        <xsl:with-param name="show-access-rights">yes</xsl:with-param>
      </xsl:apply-templates>
<!-- For DataCite schema version >= 3 -->
      <xsl:apply-templates select="*[local-name() = 'rightsList']">
        <xsl:with-param name="show-access-rights">yes</xsl:with-param>
      </xsl:apply-templates>

<!-- Distribution -->

      <xsl:variable name="distribution">
<!-- Sizes -->
        <xsl:apply-templates select="*[local-name() = 'sizes']/*[local-name() = 'size']"/>
<!-- Formats-->
        <xsl:apply-templates select="*[local-name() = 'formats']/*[local-name() = 'format']"/>
<!-- Rights -->
<!-- For DataCite schema version < 3 -->
        <xsl:apply-templates select="*[local-name() = 'rights']">
          <xsl:with-param name="show-licence">yes</xsl:with-param>
          <xsl:with-param name="show-rights">yes</xsl:with-param>
        </xsl:apply-templates>
<!-- For DataCite schema version >= 3 -->
        <xsl:apply-templates select="*[local-name() = 'rightsList']">
          <xsl:with-param name="show-licence">yes</xsl:with-param>
          <xsl:with-param name="show-rights">yes</xsl:with-param>
        </xsl:apply-templates>
        <xsl:if test="$ResourceUri != ''">
          <xsl:choose>
            <xsl:when test="$ResourceType = 'dataset'">
              <dcat:accessURL rdf:resource="{$ResourceUri}"/>
            </xsl:when>
            <xsl:otherwise>
<!--            
              <foaf:page rdf:resource="{$ResourceUri}"/>
-->
            </xsl:otherwise>
          </xsl:choose>
        </xsl:if>
      </xsl:variable>
      
      <xsl:choose>
        <xsl:when test="$ResourceType = 'dataset'">
          <dcat:distribution>
            <dcat:Distribution>
              <xsl:copy-of select="$distribution"/>
            </dcat:Distribution>
          </dcat:distribution>
        </xsl:when>
        <xsl:otherwise>
          <xsl:copy-of select="$distribution"/>
        </xsl:otherwise>
      </xsl:choose>
      
      
    </xsl:param>

<!-- Generating the output record. -->
    
    <xsl:if test="$profile = 'extended' or ($profile = 'core' and $ResourceType = 'dataset')">
    
    <xsl:choose>
      <xsl:when test="$ResourceUri != ''">
        <xsl:choose>
          <xsl:when test="$MetadataUri != ''">
            <rdf:Description rdf:about="{$MetadataUri}">
              <rdf:type rdf:resource="{$dcat}CatalogRecord"/>
              <foaf:primaryTopic rdf:resource="{$ResourceUri}"/>
              <xsl:copy-of select="$MetadataDescription"/>
            </rdf:Description>
          </xsl:when>
          <xsl:otherwise>
            <xsl:if test="normalize-space($MetadataDescription)">
              <rdf:Description>
                <rdf:type rdf:resource="{$dcat}CatalogRecord"/>
                <foaf:primaryTopic rdf:resource="{$ResourceUri}"/>
                <xsl:copy-of select="$MetadataDescription"/>
              </rdf:Description>
            </xsl:if>
          </xsl:otherwise>
        </xsl:choose>
        <rdf:Description rdf:about="{$ResourceUri}">
          <xsl:copy-of select="$ResourceDescription"/>
        </rdf:Description>
      </xsl:when>
      <xsl:otherwise>
        <rdf:Description>
          <xsl:if test="normalize-space($MetadataDescription)">
            <foaf:isPrimaryTopicOf>
              <rdf:Description>
                <rdf:type rdf:resource="{$dcat}CatalogRecord"/>
                <xsl:copy-of select="$MetadataDescription"/>
              </rdf:Description>
            </foaf:isPrimaryTopicOf>
          </xsl:if>
          <xsl:copy-of select="$ResourceDescription"/>
        </rdf:Description>
      </xsl:otherwise>
    </xsl:choose>

    <xsl:if test="$profile = 'extended'">

    <xsl:for-each select="//*[local-name() = 'fundingReferences']/*[local-name() = 'fundingReference' and normalize-space(*[local-name() = 'awardNumber']/@awardURI) != '']">
      <xsl:call-template name="FundingAwards"/>
    </xsl:for-each>

    <xsl:for-each select="//*[local-name() = 'fundingReferences']/*[local-name() = 'fundingReference' and ( starts-with(translate(normalize-space(*[local-name() = 'funderIdentifier']),$uppercase,$lowercase),'http://') or starts-with(translate(normalize-space(*[local-name() = 'funderIdentifier']),$uppercase,$lowercase),'https://') ) and not(*[local-name() = 'funderIdentifier']=preceding::*)]">
      <xsl:call-template name="Funders"/>
    </xsl:for-each>

    </xsl:if>
    
    </xsl:if>
        
  </xsl:template>

<!-- 

  DataCite elements templates
  ===========================
 
 -->


<!-- Titles template -->

  <xsl:template name="Titles" match="*[local-name() = 'titles']/*[local-name() = 'title']">
    <xsl:variable name="title" select="normalize-space(.)"/>
    <xsl:variable name="type" select="normalize-space(translate(@titleType,$uppercase,$lowercase))"/>
    <xsl:choose>
      <xsl:when test="$type = ''">
        <xsl:choose>
          <xsl:when test="normalize-space(@xml:lang) != ''">
            <dct:title xml:lang="{@xml:lang}"><xsl:value-of select="$title"/></dct:title>
          </xsl:when>
          <xsl:otherwise>
            <dct:title><xsl:value-of select="$title"/></dct:title>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:when test="$type = 'alternativetitle'">
        <xsl:choose>
          <xsl:when test="normalize-space(@xml:lang) != ''">
            <dct:alternative xml:lang="{@xml:lang}"><xsl:value-of select="$title"/></dct:alternative>
          </xsl:when>
          <xsl:otherwise>
            <dct:alternative><xsl:value-of select="$title"/></dct:alternative>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
<!-- TBD
      <xsl:when test="$type = 'subtitle' and $profile = 'extended'">
        <xsl:choose>
          <xsl:when test="normalize-space(@xml:lang) != ''">
            <dct:?? xml:lang="{@xml:lang}"><xsl:value-of select="$title"/></dct:??>
          </xsl:when>
          <xsl:otherwise>
            <dct:??><xsl:value-of select="$title"/></dct:??>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
-->
<!-- Unstable -->
      <xsl:when test="$type = 'translated'">
        <xsl:choose>
          <xsl:when test="normalize-space(@xml:lang) != ''">
            <dct:title xml:lang="{@xml:lang}"><xsl:value-of select="$title"/></dct:title>
          </xsl:when>
          <xsl:otherwise>
            <dct:title><xsl:value-of select="$title"/></dct:title>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
        
    </xsl:choose>
  </xsl:template>

<!-- Descriptions template -->

  <xsl:template name="Descriptions" match="*[local-name() = 'descriptions']/*[local-name() = 'description']">
    <xsl:variable name="description" select="normalize-space(.)"/>
    <xsl:variable name="type" select="normalize-space(translate(@descriptionType,$uppercase,$lowercase))"/>
    <xsl:choose>
      <xsl:when test="$type = 'abstract'">
        <xsl:choose>
          <xsl:when test="normalize-space(@xml:lang) != ''">
            <dct:description xml:lang="{@xml:lang}"><xsl:value-of select="$description"/></dct:description>
          </xsl:when>
          <xsl:otherwise>
            <dct:description><xsl:value-of select="$description"/></dct:description>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:when test="$type = 'methods'">
        <dct:provenance>
          <dct:ProvenanceStatement>
            <xsl:choose>
              <xsl:when test="normalize-space(@xml:lang) != ''">
                <rdfs:label xml:lang="{@xml:lang}"><xsl:value-of select="$description"/></rdfs:label>
              </xsl:when>
              <xsl:otherwise>
                <rdfs:label><xsl:value-of select="$description"/></rdfs:label>
              </xsl:otherwise>
            </xsl:choose>
          </dct:ProvenanceStatement>
        </dct:provenance>
      </xsl:when>
<!-- TBD
      <xsl:when test="$type = 'seriesinformation' and $profile = 'extended'">
        <dct:?? xml:lang="{@xml:lang}"><xsl:value-of select="$description"/></dct:??>
      </xsl:when>
-->
      <xsl:when test="$type = 'tableofcontents' and $profile = 'extended'">
        <dct:tableOfContents><xsl:value-of select="$description"/></dct:tableOfContents>
      </xsl:when>
<!--      
      <xsl:when test="$type = 'other' and $profile = 'extended'">
        <rdfs:comment xml:lang="{@xml:lang}"><xsl:value-of select="$description"/></rdfs:comment>
      </xsl:when>
-->
<!-- The following is meant to deal also with $type = 'other', and ensures that a dct:description is provided in 
     the resulting record. -->
      <xsl:otherwise>
        <xsl:choose>
          <xsl:when test="not(../*[local-name() = 'description' and $type = 'abstract'])">
            <xsl:choose>
              <xsl:when test="normalize-space(@xml:lang) != ''">
                <dct:description xml:lang="{@xml:lang}"><xsl:value-of select="$description"/></dct:description>
              </xsl:when>
              <xsl:otherwise>
                <dct:description><xsl:value-of select="$description"/></dct:description>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:when>
          <xsl:otherwise>
            <xsl:choose>
              <xsl:when test="normalize-space(@xml:lang) != ''">
                <rdfs:comment xml:lang="{@xml:lang}"><xsl:value-of select="$description"/></rdfs:comment>
              </xsl:when>
              <xsl:otherwise>
                <rdfs:comment><xsl:value-of select="$description"/></rdfs:comment>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

<!-- Subjects template -->

  <xsl:template name="Subjects" match="*[local-name() = 'subjects']/*[local-name() = 'subject']">
    <xsl:variable name="subject" select="normalize-space(.)"/>
    <xsl:variable name="subjectScheme" select="normalize-space(@subjectScheme)"/>
    <xsl:variable name="subjectSchemeLC" select="translate($subjectScheme,$uppercase,$lowercase)"/>
    <xsl:variable name="schemeURI" select="@schemeURI"/>
    <xsl:choose>
      <xsl:when test="starts-with($subject, 'http://') or starts-with($subject, 'https://')">
        <xsl:choose>
	  <xsl:when test="starts-with($subject, 'http://publications.europa.eu/resource/authority/theme/')">
            <dcat:theme rdf:resource="{$subject}"/>
	  </xsl:when>
          <xsl:otherwise>
            <dct:subject rdf:resource="{$subject}"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:when test="$subjectScheme != '' or $schemeURI != ''">
        <dct:subject>
          <skos:Concept>
            <xsl:choose>
              <xsl:when test="normalize-space(@xml:lang) != ''">
                <skos:prefLabel xml:lang="{@xml:lang}"><xsl:value-of select="$subject"/></skos:prefLabel>
              </xsl:when>
              <xsl:otherwise>
                <skos:prefLabel><xsl:value-of select="$subject"/></skos:prefLabel>
              </xsl:otherwise>
            </xsl:choose>
            <skos:inScheme>
              <xsl:choose>
                <xsl:when test="$subjectScheme != '' and $schemeURI != ''">
                  <skos:ConceptScheme rdf:about="{$schemeURI}">
		    <xsl:choose>
		      <xsl:when test="normalize-space(@xml:lang) != ''">
			<dct:title xml:lang="{@xml:lang}"><xsl:value-of select="$subjectScheme"/></dct:title>
		      </xsl:when>
		      <xsl:otherwise>
			<dct:title><xsl:value-of select="$subjectScheme"/></dct:title>
		      </xsl:otherwise>
		    </xsl:choose>
                  </skos:ConceptScheme>
                </xsl:when>
                <xsl:when test="not($subjectScheme != '') and $schemeURI != ''">
                  <skos:ConceptScheme rdf:about="{$schemeURI}"/>
                </xsl:when>
                <xsl:when test="$subjectScheme != '' and not($schemeURI != '')">
                  <skos:ConceptScheme>
		    <xsl:choose>
		      <xsl:when test="normalize-space(@xml:lang) != ''">
			<dct:title xml:lang="{@xml:lang}"><xsl:value-of select="$subjectScheme"/></dct:title>
		      </xsl:when>
		      <xsl:otherwise>
			<dct:title><xsl:value-of select="$subjectScheme"/></dct:title>
		      </xsl:otherwise>
		    </xsl:choose>
                  </skos:ConceptScheme>
                </xsl:when>
              </xsl:choose>
            </skos:inScheme>
          </skos:Concept>
        </dct:subject>
      </xsl:when>
      <xsl:otherwise>
        <xsl:choose>
          <xsl:when test="normalize-space(@xml:lang) != ''">
            <dcat:keyword xml:lang="{@xml:lang}"><xsl:value-of select="$subject"/></dcat:keyword>
          </xsl:when>
          <xsl:otherwise>
            <dcat:keyword><xsl:value-of select="$subject"/></dcat:keyword>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


<!-- Funding references template -->

  <xsl:template name="FundingReferences">
    <xsl:param name="funderIdentifier" select="normalize-space(*[local-name() = 'funderIdentifier'])"/>
    <xsl:param name="funderIdentifierType" select="translate(normalize-space(*[local-name() = 'funderIdentifier']/@funderIdentifierType),$uppercase,$lowercase)"/>
    <xsl:param name="funderURI">
      <xsl:variable name="uri">
        <xsl:call-template name="IdentifierURI">
          <xsl:with-param name="identifier" select="$funderIdentifier"/>
          <xsl:with-param name="type" select="$funderIdentifierType"/>
<!--          
          <xsl:with-param name="schemeURI" select="$schemeURI"/>
-->
        </xsl:call-template>
      </xsl:variable>
      <xsl:if test="starts-with(translate(normalize-space($uri),$uppercase,$lowercase),'http://') or starts-with(translate(normalize-space($uri),$uppercase,$lowercase),'https://') or starts-with(translate(normalize-space($uri),$uppercase,$lowercase),'urn://')">
        <xsl:value-of select="$uri"/>
      </xsl:if>
<!--    
      <xsl:if test="starts-with(translate(normalize-space(*[local-name() = 'funderIdentifier']),$uppercase,$lowercase),'http://') or starts-with(translate(normalize-space(*[local-name() = 'funderIdentifier']),$uppercase,$lowercase),'https://')">
        <xsl:value-of select="normalize-space(*[local-name() = 'funderIdentifier'])"/>
      </xsl:if>
-->
    </xsl:param>
    <xsl:param name="funderInfo">
      <dct:identifier><xsl:value-of select="normalize-space(*[local-name() = 'funderIdentifier'])"/></dct:identifier>
      <foaf:name><xsl:value-of select="normalize-space(*[local-name() = 'funderName'])"/></foaf:name>
    </xsl:param>
    <xsl:param name="fundingReferenceURI">
      <xsl:value-of select="normalize-space(*[local-name() = 'awardNumber']/@awardURI)"/>
    </xsl:param>
    <xsl:choose>
      <xsl:when test="$fundingReferenceURI != ''">
        <frapo:isFundedBy rdf:resource="{$fundingReferenceURI}"/>
      </xsl:when>
      <xsl:when test="normalize-space(*[local-name() = 'awardNumber']) != '' or normalize-space(*[local-name() = 'awardTitle']) != ''">
        <frapo:isFundedBy>
          <xsl:call-template name="FundingAwards"/>
        </frapo:isFundedBy>
      </xsl:when>
    </xsl:choose>
    <xsl:choose>
      <xsl:when test="$funderURI != ''">
        <schema:funder rdf:resource="{$funderURI}"/>
      </xsl:when>
      <xsl:when test="normalize-space($funderInfo) != ''">
        <schema:funder>
          <xsl:call-template name="Funders"/>
        </schema:funder>
      </xsl:when>
    </xsl:choose>
  </xsl:template>
  
<!-- Version template -->

  <xsl:template name="Version" match="*[local-name() = 'version']">
    <owl:versionInfo><xsl:value-of select="normalize-space(.)"/></owl:versionInfo>
  </xsl:template>

<!-- Rights template -->

  <xsl:template name="Rights" match="*[local-name() = 'rights']">
    <xsl:param name="show-licence"/>
    <xsl:param name="show-access-rights"/>
    <xsl:param name="show-rights"/>
    <xsl:param name="rightsText" select="normalize-space(.)"/>
    <xsl:param name="rightsURI" select="normalize-space(@rightsURI)"/>
    <xsl:param name="rightsLabel">
      <xsl:choose>
        <xsl:when test="normalize-space(@xml:lang) != ''">
          <rdfs:label xml:lang="{@xml:lang}"><xsl:value-of select="$rightsText"/></rdfs:label>
        </xsl:when>
        <xsl:otherwise>
          <rdfs:label><xsl:value-of select="$rightsText"/></rdfs:label>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:param>
<!-- Added in DataCite v4.2 -->
    <xsl:param name="rightsIdentifier" select="normalize-space(@rightsIdentifier)"/>
<!-- Added in DataCite v4.2 -->
    <xsl:param name="rightsIdentifierScheme" select="normalize-space(@rightsIdentifierScheme)"/>
<!-- Added in DataCite v4.2 -->
    <xsl:param name="rightsIdentifierSchemeURI" select="normalize-space(@schemeURI)"/>
    <xsl:param name="rightsID">
      <xsl:if test="$rightsIdentifier != ''">
        <adms:identifier>
          <adms:Identifier>
            <skos:notation><xsl:value-of select="$rightsIdentifier"/></skos:notation>
            <xsl:choose>
              <xsl:when test="$rightsIdentifierScheme != ''">
                <adms:schemeAgency><xsl:value-of select="$rightsIdentifierScheme"/></adms:schemeAgency>
              </xsl:when>
              <xsl:when test="$rightsIdentifierSchemeURI != ''">
                <dct:creator rdf:resource="{$rightsIdentifierSchemeURI}"/>
              </xsl:when>
            </xsl:choose>
          </adms:Identifier>
        </adms:identifier>
      </xsl:if>
    </xsl:param>
    <xsl:param name="licence">
      <xsl:if test="$rightsURI != ''">
<!--      
        <xsl:if test="$show-use-conditions = 'yes'">
<rdfs:label><xsl:value-of select="$rightsURI"/></rdfs:label>
-->
        <xsl:choose>
          <xsl:when test="starts-with($rightsURI, 'http://creativecommons.org/')">
            <dct:license rdf:resource="{$rightsURI}"/>
          </xsl:when>
          <xsl:when test="starts-with($rightsURI, 'https://creativecommons.org/')">
            <dct:license rdf:resource="{$rightsURI}"/>
          </xsl:when>
          <xsl:when test="starts-with($rightsURI, $oplic)">
            <dct:license rdf:resource="{$rightsURI}"/>
          </xsl:when>
          <xsl:otherwise>not-detected</xsl:otherwise>
        </xsl:choose>
<!--            
        </xsl:if>
        <xsl:if test="$show-access-conditions = 'yes'">        
          <xsl:choose>
-->
      </xsl:if>
    </xsl:param>
    <xsl:param name="access-rights">       
      <xsl:if test="$rightsURI != ''">
<!-- 
  See: 
  - https://wiki.surfnet.nl/display/standards/info-eu-repo#info-eu-repo-AccessRights 
  - http://guidelines.readthedocs.io/en/latest/data/field_rights.html
-->
        <xsl:choose>
          <xsl:when test="starts-with($rightsURI,'info:eu-repo/semantics/closedAccess')">
            <dct:accessRights rdf:resource="{$opar}NON_PUBLIC"/>
            <dct:accessRights>
              <dct:RightsStatement rdf:about="{$rightsURI}">
                <xsl:copy-of select="$rightsLabel"/>
              </dct:RightsStatement>
            </dct:accessRights>
          </xsl:when>
          <xsl:when test="starts-with($rightsURI,'info:eu-repo/semantics/embargoedAccess')">
            <dct:accessRights rdf:resource="{$opar}NON_PUBLIC"/>
            <dct:accessRights>
              <dct:RightsStatement rdf:about="{$rightsURI}">
                <xsl:copy-of select="$rightsLabel"/>
              </dct:RightsStatement>
            </dct:accessRights>
          </xsl:when>
          <xsl:when test="starts-with($rightsURI,'info:eu-repo/semantics/restrictedAccess')">
            <dct:accessRights rdf:resource="{$opar}RESTRICTED"/>
            <dct:accessRights>
              <dct:RightsStatement rdf:about="{$rightsURI}">
                <xsl:copy-of select="$rightsLabel"/>
              </dct:RightsStatement>
            </dct:accessRights>
          </xsl:when>
          <xsl:when test="starts-with($rightsURI,'info:eu-repo/semantics/openAccess')">
            <dct:accessRights rdf:resource="{$opar}PUBLIC"/>
            <dct:accessRights>
              <dct:RightsStatement rdf:about="{$rightsURI}">
                <xsl:copy-of select="$rightsLabel"/>
              </dct:RightsStatement>
            </dct:accessRights>
          </xsl:when>
        
<!-- See: http://www.ukoln.ac.uk/repositories/digirep/index/Eprints_AccessRights_Vocabulary_Encoding_Scheme -->
          <xsl:when test="starts-with($rightsURI,'http://purl.org/eprint/accessRights/ClosedAccess')">
            <dct:accessRights rdf:resource="{$opar}NON_PUBLIC"/>
            <dct:accessRights>
              <dct:RightsStatement rdf:about="{$rightsURI}">
                <xsl:copy-of select="$rightsLabel"/>
              </dct:RightsStatement>
            </dct:accessRights>
          </xsl:when>
          <xsl:when test="starts-with($rightsURI,'http://purl.org/eprint/accessRights/RestrictedAccess')">
            <dct:accessRights rdf:resource="{$opar}RESTRICTED"/>
            <dct:accessRights>
              <dct:RightsStatement rdf:about="{$rightsURI}">
                <xsl:copy-of select="$rightsLabel"/>
              </dct:RightsStatement>
            </dct:accessRights>
          </xsl:when>
          <xsl:when test="starts-with($rightsURI,'http://purl.org/eprint/accessRights/OpenAccess')">
            <dct:accessRights rdf:resource="{$opar}PUBLIC"/>
            <dct:accessRights>
              <dct:RightsStatement rdf:about="{$rightsURI}">
                <xsl:copy-of select="$rightsLabel"/>
              </dct:RightsStatement>
            </dct:accessRights>
          </xsl:when>

          <xsl:when test="starts-with($rightsURI,$opar)">
            <dct:accessRights rdf:resource="{$rightsURI}"/>
          </xsl:when>
          <xsl:otherwise>not-detected</xsl:otherwise>
        </xsl:choose>
      </xsl:if>
    </xsl:param>
    <xsl:param name="rights">
      <xsl:choose>
        <xsl:when test="$rightsURI != ''">
          <dct:rights>
            <dct:RightsStatement rdf:about="{$rightsURI}">
              <xsl:copy-of select="$rightsLabel"/>
              <xsl:copy-of select="$rightsID"/>
            </dct:RightsStatement>
          </dct:rights>
        </xsl:when>
        <xsl:otherwise>
          <dct:rights>
            <dct:RightsStatement>
              <xsl:copy-of select="$rightsLabel"/>
              <xsl:copy-of select="$rightsID"/>
            </dct:RightsStatement>
          </dct:rights>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:param>
    <xsl:choose>
      <xsl:when test="$licence != 'not-detected' or $access-rights != 'not-detected'">
        <xsl:if test="$licence != 'not-detected' and $show-licence = 'yes'">
          <xsl:copy-of select="$licence"/>
        </xsl:if>
        <xsl:if test="$access-rights != 'not-detected' and $show-access-rights = 'yes'">
          <xsl:copy-of select="$access-rights"/>
        </xsl:if>
      </xsl:when>
      <xsl:when test="$show-rights = 'yes'">
        <xsl:copy-of select="$rights"/>
      </xsl:when>
    </xsl:choose>
<!--      
    <dct:rights>
      <xsl:choose>
        <xsl:when test="$rightsURI != ''">
          <dct:RightsStatement rdf:about="{$rightsURI}">
            <xsl:copy-of select="$rightsLabel"/>
          </dct:RightsStatement>
        </xsl:when>
        <xsl:otherwise>
          <dct:RightsStatement>
            <xsl:copy-of select="$rightsLabel"/>
          </dct:RightsStatement>
        </xsl:otherwise>
      </xsl:choose>
    </dct:rights>
-->
  </xsl:template>

<!-- Rights list template -->

  <xsl:template name="RightsList" match="*[local-name() = 'rightsList']">
    <xsl:param name="show-licence"/>
    <xsl:param name="show-access-rights"/>
    <xsl:param name="show-rights"/>
    <xsl:apply-templates select="*[local-name() = 'rights']">
      <xsl:with-param name="show-licence" select="$show-licence"/>
      <xsl:with-param name="show-access-rights" select="$show-access-rights"/>
      <xsl:with-param name="show-rights" select="$show-rights"/>
    </xsl:apply-templates>
  </xsl:template>

<!-- Geolocations template -->

  <xsl:template name="Geolocations" match="*[local-name() = 'geoLocations']/*[local-name() = 'geoLocation']">
  
    <xsl:param name="place" select="normalize-space(*[local-name() = 'geoLocationPlace'])"/>

    <xsl:param name="point">
      <xsl:if test="normalize-space(*[local-name() = 'geoLocationPoint']) != ''">
        <xsl:choose>
          <xsl:when test="*[local-name() = 'geoLocationPoint']/*[local-name() = 'pointLatitude'] and *[local-name() = 'geoLocationPoint']/*[local-name() = 'pointLongitude']">
            <xsl:value-of select="normalize-space(concat(*[local-name() = 'geoLocationPoint']/*[local-name() = 'pointLatitude'],' ',*[local-name() = 'geoLocationPoint']/*[local-name() = 'pointLongitude']))"/>
          </xsl:when>
          <xsl:when test="self::text()">
            <xsl:value-of select="normalize-space(translate(*[local-name() = 'geoLocationPoint'],',',' '))"/>
          </xsl:when>
        </xsl:choose>
      </xsl:if>
    </xsl:param>
    
    <xsl:param name="pointLongitude" select="normalize-space(*[local-name() = 'geoLocationPoint']/*[local-name() = 'pointLongitude'])"/>

    <xsl:param name="pointLatitude" select="normalize-space(*[local-name() = 'geoLocationPoint']/*[local-name() = 'pointLatitude'])"/>

    <xsl:param name="box">
      <xsl:if test="normalize-space(*[local-name() = 'geoLocationBox']) != ''">
        <xsl:choose>
          <xsl:when test="*[local-name() = 'geoLocationBox']/*[local-name() = 'northBoundLatitude'] and *[local-name() = 'geoLocationBox']/*[local-name() = 'southBoundLatitude'] and *[local-name() = 'geoLocationBox']/*[local-name() = 'eastBoundLongitude'] and *[local-name() = 'geoLocationBox']/*[local-name() = 'westBoundLongitude']">
            <xsl:value-of select="normalize-space(concat(*[local-name() = 'geoLocationBox']/*[local-name() = 'southBoundLatitude'],' ',*[local-name() = 'geoLocationBox']/*[local-name() = 'westBoundLongitude'],' ',*[local-name() = 'geoLocationBox']/*[local-name() = 'northBoundLatitude'],' ',*[local-name() = 'geoLocationBox']/*[local-name() = 'eastBoundLongitude']))"/>
          </xsl:when>
          <xsl:when test="self::text()">
            <xsl:value-of select="normalize-space(translate(*[local-name() = 'geoLocationBox'],',',' '))"/>
          </xsl:when>
        </xsl:choose>
      </xsl:if>
    </xsl:param>
    
    <xsl:param name="north">
      <xsl:choose>
        <xsl:when test="*[local-name() = 'geoLocationBox']/*[local-name() = 'northBoundLatitude']">
          <xsl:value-of select="normalize-space(*[local-name() = 'geoLocationBox']/*[local-name() = 'northBoundLatitude'])"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="substring-before($box, ' ')"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:param>
    <xsl:param name="esw" select="substring-after($box, ' ')"/>
    <xsl:param name="sw" select="substring-after($esw, ' ')"/>
    <xsl:param name="east">
      <xsl:choose>
        <xsl:when test="*[local-name() = 'geoLocationBox']/*[local-name() = 'eastBoundLongitude']">
          <xsl:value-of select="normalize-space(*[local-name() = 'geoLocationBox']/*[local-name() = 'eastBoundLongitude'])"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="substring-before($esw, ' ')"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:param>
    <xsl:param name="south">
      <xsl:choose>
        <xsl:when test="*[local-name() = 'geoLocationBox']/*[local-name() = 'southBoundLatitude']">
          <xsl:value-of select="normalize-space(*[local-name() = 'geoLocationBox']/*[local-name() = 'southBoundLatitude'])"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="substring-before($sw, ' ')"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:param>
    <xsl:param name="west">
      <xsl:choose>
        <xsl:when test="*[local-name() = 'geoLocationBox']/*[local-name() = 'westBoundLongitude']">
          <xsl:value-of select="normalize-space(*[local-name() = 'geoLocationBox']/*[local-name() = 'westBoundLongitude'])"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="substring-after($sw, ' ')"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:param>

    <xsl:param name="polygonAsLonLat">
      <xsl:for-each select="*[local-name() = 'geoLocationPolygon']">
        <xsl:variable name="cnr" select="count(*[local-name() = 'polygonPoint'])"/>
        <xsl:for-each select="*[local-name() = 'polygonPoint']">
          <xsl:variable name="delimiter">
            <xsl:if test="position() &lt; $cnr">
              <xsl:text>,</xsl:text>
            </xsl:if>
          </xsl:variable>
          <xsl:value-of select="normalize-space(*[local-name() = 'pointLongitude'])"/><xsl:text> </xsl:text><xsl:value-of select="normalize-space(*[local-name() = 'pointLatitude'])"/><xsl:value-of select="$delimiter"/>
        </xsl:for-each>
      </xsl:for-each>
    </xsl:param>
    
    <xsl:param name="polygonAsLatLon">
      <xsl:for-each select="*[local-name() = 'geoLocationPolygon']">
        <xsl:variable name="cnr" select="count(*[local-name() = 'polygonPoint'])"/>
        <xsl:for-each select="*[local-name() = 'polygonPoint']">
          <xsl:variable name="delimiter">
            <xsl:if test="position() &lt; $cnr">
              <xsl:text>,</xsl:text>
            </xsl:if>
          </xsl:variable>
          <xsl:value-of select="normalize-space(*[local-name() = 'pointLatitude'])"/><xsl:text> </xsl:text><xsl:value-of select="normalize-space(*[local-name() = 'pointLongitude'])"/><xsl:value-of select="$delimiter"/>
        </xsl:for-each>
      </xsl:for-each>
    </xsl:param>

    <xsl:param name="polygon">
      <xsl:choose>
        <xsl:when test="$SrsAxisOrder = 'LatLon'">
          <xsl:value-of select="$polygonAsLatLon"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="$polygonAsLonLat"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:param>
    
<!-- Geometry as GML (GeoSPARQL) -->

    <xsl:param name="pointAsGMLLiteral">
      <xsl:if test="$point != ''">
        <xsl:choose>
          <xsl:when test="$SrsAxisOrder = 'LatLon'">&lt;gml:Point srsName="<xsl:value-of select="$SrsUri"/>"&gt;&lt;gml:pos srsDimension="2"&gt;<xsl:value-of select="$pointLatitude"/><xsl:text> </xsl:text><xsl:value-of select="$pointLongitude"/>&lt;/gml:pos&gt;&lt;/gml:Point&gt;</xsl:when>
          <xsl:otherwise>&lt;gml:Point srsName="<xsl:value-of select="$SrsUri"/>"&gt;&lt;gml:pos srsDimension="2"&gt;<xsl:value-of select="$pointLongitude"/><xsl:text> </xsl:text><xsl:value-of select="$pointLatitude"/>&lt;/gml:pos&gt;&lt;/gml:Point&gt;</xsl:otherwise>
        </xsl:choose>
      </xsl:if>
    </xsl:param>

    <xsl:param name="boxAsGMLLiteral">
      <xsl:if test="$box != ''">
        <xsl:choose>
          <xsl:when test="$SrsUri = 'http://www.opengis.net/def/crs/OGC/1.3/CRS84'">&lt;gml:Envelope srsName="<xsl:value-of select="$SrsUri"/>"&gt;&lt;gml:lowerCorner&gt;<xsl:value-of select="$west"/><xsl:text> </xsl:text><xsl:value-of select="$south"/>&lt;/gml:lowerCorner&gt;&lt;gml:upperCorner&gt;<xsl:value-of select="$east"/><xsl:text> </xsl:text><xsl:value-of select="$north"/>&lt;/gml:upperCorner&gt;&lt;/gml:Envelope&gt;</xsl:when>
          <xsl:when test="$SrsAxisOrder = 'LonLat'">&lt;gml:Envelope srsName="<xsl:value-of select="$SrsUri"/>"&gt;&lt;gml:lowerCorner&gt;<xsl:value-of select="$west"/><xsl:text> </xsl:text><xsl:value-of select="$south"/>&lt;/gml:lowerCorner&gt;&lt;gml:upperCorner&gt;<xsl:value-of select="$east"/><xsl:text> </xsl:text><xsl:value-of select="$north"/>&lt;/gml:upperCorner&gt;&lt;/gml:Envelope&gt;</xsl:when>
          <xsl:when test="$SrsAxisOrder = 'LatLon'">&lt;gml:Envelope srsName="<xsl:value-of select="$SrsUri"/>"&gt;&lt;gml:lowerCorner&gt;<xsl:value-of select="$south"/><xsl:text> </xsl:text><xsl:value-of select="$west"/>&lt;/gml:lowerCorner&gt;&lt;gml:upperCorner&gt;<xsl:value-of select="$north"/><xsl:text> </xsl:text><xsl:value-of select="$east"/>&lt;/gml:upperCorner&gt;&lt;/gml:Envelope&gt;</xsl:when>
        </xsl:choose>
      </xsl:if>
    </xsl:param>

    <xsl:param name="polygonAsGMLLiteral">
      <xsl:if test="$polygon != ''">
        <xsl:choose>
          <xsl:when test="$SrsUri = 'http://www.opengis.net/def/crs/OGC/1.3/CRS84'">&lt;gml:Polygon srsName="<xsl:value-of select="$SrsUri"/>"&gt;&lt;gml:exterior&gt;&lt;gml:LinearRing&gt;&lt;gml:posList srsDimension="2"&gt;<xsl:value-of select="translate($polygon,',',' ')"/>&lt;/gml:posList&gt;&lt;/gml:LinearRing&gt;&lt;/gml:exterior&gt;&lt;/gml:Polygon&gt;</xsl:when>
          <xsl:otherwise>&lt;gml:Polygon srsName="<xsl:value-of select="$SrsUri"/>"&gt;&lt;gml:exterior&gt;&lt;gml:LinearRing&gt;&lt;gml:posList srsDimension="2"&gt;<xsl:value-of select="translate($polygon,',',' ')"/>&lt;/gml:posList&gt;&lt;/gml:LinearRing&gt;&lt;/gml:exterior&gt;&lt;/gml:Polygon&gt;</xsl:otherwise>
        </xsl:choose>
      </xsl:if>
    </xsl:param>
<!--
    <xsl:param name="GMLLiteral">
      <xsl:choose>
        <xsl:when test="$point != ''">
          <xsl:choose>
            <xsl:when test="$SrsAxisOrder = 'LatLon'">&lt;gml:Point srsName="<xsl:value-of select="$SrsUri"/>"&gt;&lt;gml:pos srsDimension="2"&gt;<xsl:value-of select="$pointLatitude"/><xsl:text> </xsl:text><xsl:value-of select="$pointLongitude"/>&lt;/gml:pos&gt;&lt;/gml:Point&gt;</xsl:when>
            <xsl:otherwise>&lt;gml:Point srsName="<xsl:value-of select="$SrsUri"/>"&gt;&lt;gml:pos srsDimension="2"&gt;<xsl:value-of select="$pointLongitude"/><xsl:text> </xsl:text><xsl:value-of select="$pointLatitude"/>&lt;/gml:pos&gt;&lt;/gml:Point&gt;</xsl:otherwise>
          </xsl:choose>
        </xsl:when>
        <xsl:when test="$box != ''">
          <xsl:choose>
            <xsl:when test="$SrsUri = 'http://www.opengis.net/def/crs/OGC/1.3/CRS84'">&lt;gml:Envelope srsName="<xsl:value-of select="$SrsUri"/>"&gt;&lt;gml:lowerCorner&gt;<xsl:value-of select="$west"/><xsl:text> </xsl:text><xsl:value-of select="$south"/>&lt;/gml:lowerCorner&gt;&lt;gml:upperCorner&gt;<xsl:value-of select="$east"/><xsl:text> </xsl:text><xsl:value-of select="$north"/>&lt;/gml:upperCorner&gt;&lt;/gml:Envelope&gt;</xsl:when>
            <xsl:when test="$SrsAxisOrder = 'LonLat'">&lt;gml:Envelope srsName="<xsl:value-of select="$SrsUri"/>"&gt;&lt;gml:lowerCorner&gt;<xsl:value-of select="$west"/><xsl:text> </xsl:text><xsl:value-of select="$south"/>&lt;/gml:lowerCorner&gt;&lt;gml:upperCorner&gt;<xsl:value-of select="$east"/><xsl:text> </xsl:text><xsl:value-of select="$north"/>&lt;/gml:upperCorner&gt;&lt;/gml:Envelope&gt;</xsl:when>
            <xsl:when test="$SrsAxisOrder = 'LatLon'">&lt;gml:Envelope srsName="<xsl:value-of select="$SrsUri"/>"&gt;&lt;gml:lowerCorner&gt;<xsl:value-of select="$south"/><xsl:text> </xsl:text><xsl:value-of select="$west"/>&lt;/gml:lowerCorner&gt;&lt;gml:upperCorner&gt;<xsl:value-of select="$north"/><xsl:text> </xsl:text><xsl:value-of select="$east"/>&lt;/gml:upperCorner&gt;&lt;/gml:Envelope&gt;</xsl:when>
          </xsl:choose>
        </xsl:when>
        <xsl:when test="$polygon != ''">
          <xsl:choose>
            <xsl:when test="$SrsUri = 'http://www.opengis.net/def/crs/OGC/1.3/CRS84'">&lt;gml:Polygon srsName="<xsl:value-of select="$SrsUri"/>"&gt;&lt;gml:exterior&gt;&lt;gml:LinearRing&gt;&lt;gml:posList srsDimension="2"&gt;<xsl:value-of select="translate($polygon,',',' ')"/>&lt;/gml:posList&gt;&lt;/gml:LinearRing&gt;&lt;/gml:exterior&gt;&lt;/gml:Polygon&gt;</xsl:when>
            <xsl:otherwise>&lt;gml:Polygon srsName="<xsl:value-of select="$SrsUri"/>"&gt;&lt;gml:exterior&gt;&lt;gml:LinearRing&gt;&lt;gml:posList srsDimension="2"&gt;<xsl:value-of select="translate($polygon,',',' ')"/>&lt;/gml:posList&gt;&lt;/gml:LinearRing&gt;&lt;/gml:exterior&gt;&lt;/gml:Polygon&gt;</xsl:otherwise>
          </xsl:choose>
        </xsl:when>
      </xsl:choose>
    </xsl:param>
-->
<!-- Geometry as WKT (GeoSPARQL) -->

    <xsl:param name="pointAsWKTLiteral">
      <xsl:if test="$point != ''">
        <xsl:choose>
          <xsl:when test="$SrsUri = 'http://www.opengis.net/def/crs/OGC/1.3/CRS84'">POINT(<xsl:value-of select="$pointLongitude"/><xsl:text> </xsl:text><xsl:value-of select="$pointLatitude"/>)</xsl:when>
          <xsl:when test="$SrsAxisOrder = 'LonLat'">&lt;<xsl:value-of select="$SrsUri"/>&gt; POINT(<xsl:value-of select="$pointLongitude"/><xsl:text> </xsl:text><xsl:value-of select="$pointLatitude"/>)</xsl:when>
          <xsl:when test="$SrsAxisOrder = 'LatLon'">&lt;<xsl:value-of select="$SrsUri"/>&gt; POINT(<xsl:value-of select="$pointLatitude"/><xsl:text> </xsl:text><xsl:value-of select="$pointLongitude"/>)</xsl:when>
        </xsl:choose>
      </xsl:if>
    </xsl:param>

    <xsl:param name="boxAsWKTLiteral">
      <xsl:if test="$box != ''">
        <xsl:choose>
          <xsl:when test="$SrsUri = 'http://www.opengis.net/def/crs/OGC/1.3/CRS84'">POLYGON((<xsl:value-of select="$west"/><xsl:text> </xsl:text><xsl:value-of select="$north"/>,<xsl:value-of select="$east"/><xsl:text> </xsl:text><xsl:value-of select="$north"/>,<xsl:value-of select="$east"/><xsl:text> </xsl:text><xsl:value-of select="$south"/>,<xsl:value-of select="$west"/><xsl:text> </xsl:text><xsl:value-of select="$south"/>,<xsl:value-of select="$west"/><xsl:text> </xsl:text><xsl:value-of select="$north"/>))</xsl:when>
          <xsl:when test="$SrsAxisOrder = 'LonLat'">&lt;<xsl:value-of select="$SrsUri"/>&gt; POLYGON((<xsl:value-of select="$west"/><xsl:text> </xsl:text><xsl:value-of select="$north"/>,<xsl:value-of select="$east"/><xsl:text> </xsl:text><xsl:value-of select="$north"/>,<xsl:value-of select="$east"/><xsl:text> </xsl:text><xsl:value-of select="$south"/>,<xsl:value-of select="$west"/><xsl:text> </xsl:text><xsl:value-of select="$south"/>,<xsl:value-of select="$west"/><xsl:text> </xsl:text><xsl:value-of select="$north"/>))</xsl:when>
          <xsl:when test="$SrsAxisOrder = 'LatLon'">&lt;<xsl:value-of select="$SrsUri"/>&gt; POLYGON((<xsl:value-of select="$north"/><xsl:text> </xsl:text><xsl:value-of select="$west"/>,<xsl:value-of select="$north"/><xsl:text> </xsl:text><xsl:value-of select="$east"/>,<xsl:value-of select="$south"/><xsl:text> </xsl:text><xsl:value-of select="$east"/>,<xsl:value-of select="$south"/><xsl:text> </xsl:text><xsl:value-of select="$west"/>,<xsl:value-of select="$north"/><xsl:text> </xsl:text><xsl:value-of select="$west"/>))</xsl:when>
        </xsl:choose>
      </xsl:if>
    </xsl:param>

    <xsl:param name="polygonAsWKTLiteral">
      <xsl:if test="$polygon != ''">
        <xsl:choose>
          <xsl:when test="$SrsUri = 'http://www.opengis.net/def/crs/OGC/1.3/CRS84'">POLYGON((<xsl:value-of select="$polygon"/>))</xsl:when>
          <xsl:otherwise>&lt;<xsl:value-of select="$SrsUri"/>&gt; POLYGON((<xsl:value-of select="$polygon"/>))</xsl:otherwise>
        </xsl:choose>
      </xsl:if>
    </xsl:param>
<!--
    <xsl:param name="WKTLiteral">
      <xsl:choose>
        <xsl:when test="$point != ''">
          <xsl:choose>
            <xsl:when test="$SrsUri = 'http://www.opengis.net/def/crs/OGC/1.3/CRS84'">POINT(<xsl:value-of select="$pointLongitude"/><xsl:text> </xsl:text><xsl:value-of select="$pointLatitude"/>)</xsl:when>
            <xsl:when test="$SrsAxisOrder = 'LonLat'">&lt;<xsl:value-of select="$SrsUri"/>&gt; POINT(<xsl:value-of select="$pointLongitude"/><xsl:text> </xsl:text><xsl:value-of select="$pointLatitude"/>)</xsl:when>
            <xsl:when test="$SrsAxisOrder = 'LatLon'">&lt;<xsl:value-of select="$SrsUri"/>&gt; POINT(<xsl:value-of select="$pointLatitude"/><xsl:text> </xsl:text><xsl:value-of select="$pointLongitude"/>)</xsl:when>
          </xsl:choose>
        </xsl:when>
        <xsl:when test="$box != ''">
          <xsl:choose>
            <xsl:when test="$SrsUri = 'http://www.opengis.net/def/crs/OGC/1.3/CRS84'">POLYGON((<xsl:value-of select="$west"/><xsl:text> </xsl:text><xsl:value-of select="$north"/>,<xsl:value-of select="$east"/><xsl:text> </xsl:text><xsl:value-of select="$north"/>,<xsl:value-of select="$east"/><xsl:text> </xsl:text><xsl:value-of select="$south"/>,<xsl:value-of select="$west"/><xsl:text> </xsl:text><xsl:value-of select="$south"/>,<xsl:value-of select="$west"/><xsl:text> </xsl:text><xsl:value-of select="$north"/>))</xsl:when>
            <xsl:when test="$SrsAxisOrder = 'LonLat'">&lt;<xsl:value-of select="$SrsUri"/>&gt; POLYGON((<xsl:value-of select="$west"/><xsl:text> </xsl:text><xsl:value-of select="$north"/>,<xsl:value-of select="$east"/><xsl:text> </xsl:text><xsl:value-of select="$north"/>,<xsl:value-of select="$east"/><xsl:text> </xsl:text><xsl:value-of select="$south"/>,<xsl:value-of select="$west"/><xsl:text> </xsl:text><xsl:value-of select="$south"/>,<xsl:value-of select="$west"/><xsl:text> </xsl:text><xsl:value-of select="$north"/>))</xsl:when>
            <xsl:when test="$SrsAxisOrder = 'LatLon'">&lt;<xsl:value-of select="$SrsUri"/>&gt; POLYGON((<xsl:value-of select="$north"/><xsl:text> </xsl:text><xsl:value-of select="$west"/>,<xsl:value-of select="$north"/><xsl:text> </xsl:text><xsl:value-of select="$east"/>,<xsl:value-of select="$south"/><xsl:text> </xsl:text><xsl:value-of select="$east"/>,<xsl:value-of select="$south"/><xsl:text> </xsl:text><xsl:value-of select="$west"/>,<xsl:value-of select="$north"/><xsl:text> </xsl:text><xsl:value-of select="$west"/>))</xsl:when>
          </xsl:choose>
        </xsl:when>
        <xsl:when test="$polygon != ''">
          <xsl:choose>
            <xsl:when test="$SrsUri = 'http://www.opengis.net/def/crs/OGC/1.3/CRS84'">POLYGON((<xsl:value-of select="translate($polygon)"/>))</xsl:when>
            <xsl:otherwise>&lt;<xsl:value-of select="$SrsUri"/>&gt; POLYGON((<xsl:value-of select="translate($polygon)"/>))</xsl:otherwise>
          </xsl:choose>
        </xsl:when>
      </xsl:choose>
    </xsl:param>
-->
<!-- Geometry as GeoJSON -->

    <xsl:param name="pointAsGeoJSONLiteral">
      <xsl:if test="$point != ''">{"type":"Point","crs":{"type":"name","properties":{"name":"<xsl:value-of select="$SrsUrn"/>"}},"coordinates":[<xsl:value-of select="$pointLongitude"/><xsl:text>,</xsl:text><xsl:value-of select="$pointLatitude"/>]}</xsl:if>
    </xsl:param>

    <xsl:param name="boxAsGeoJSONLiteral">
      <xsl:if test="$box != ''">{"type":"Polygon","crs":{"type":"name","properties":{"name":"<xsl:value-of select="$SrsUrn"/>"}},"coordinates":[[[<xsl:value-of select="$west"/><xsl:text>,</xsl:text><xsl:value-of select="$north"/>],[<xsl:value-of select="$east"/><xsl:text>,</xsl:text><xsl:value-of select="$north"/>],[<xsl:value-of select="$east"/><xsl:text>,</xsl:text><xsl:value-of select="$south"/>],[<xsl:value-of select="$west"/><xsl:text>,</xsl:text><xsl:value-of select="$south"/>],[<xsl:value-of select="$west"/><xsl:text>,</xsl:text><xsl:value-of select="$north"/>]]]}</xsl:if>
    </xsl:param>

    <xsl:param name="polygonAsArray">
      <xsl:if test="$polygon != ''">
        <xsl:text>[</xsl:text>
        <xsl:for-each select="*[local-name() = 'geoLocationPolygon']">
          <xsl:variable name="cnr" select="count(*[local-name() = 'polygonPoint'])"/>
          <xsl:for-each select="*[local-name() = 'polygonPoint']">
            <xsl:variable name="delimiter">
              <xsl:if test="position() &lt; $cnr">
                <xsl:text>,</xsl:text>
              </xsl:if>
            </xsl:variable>
            <xsl:text>[</xsl:text><xsl:value-of select="normalize-space(*[local-name() = 'pointLatitude'])"/><xsl:text> </xsl:text><xsl:value-of select="normalize-space(*[local-name() = 'pointLongitude'])"/><xsl:value-of select="$delimiter"/><xsl:text>]</xsl:text>
          </xsl:for-each>
        </xsl:for-each>
        <xsl:text>]</xsl:text>
      </xsl:if>
    </xsl:param>
    
    <xsl:param name="polygonAsGeoJSONLiteral">
      <xsl:if test="$polygon != ''">{"type":"Polygon","crs":{"type":"name","properties":{"name":"<xsl:value-of select="$SrsUrn"/>"}},"coordinates":[[[<xsl:value-of select="$polygonAsArray"/>]]]}</xsl:if>
    </xsl:param>
<!--
    <xsl:param name="GeoJSONLiteral">
      <xsl:choose>
        <xsl:when test="$point != ''">{"type":"Point","crs":{"type":"name","properties":{"name":"<xsl:value-of select="$SrsUrn"/>"}},"coordinates":[<xsl:value-of select="$pointLongitude"/><xsl:text>,</xsl:text><xsl:value-of select="$pointLatitude"/>]}</xsl:when>
        <xsl:when test="$box != ''">{"type":"Polygon","crs":{"type":"name","properties":{"name":"<xsl:value-of select="$SrsUrn"/>"}},"coordinates":[[[<xsl:value-of select="$west"/><xsl:text>,</xsl:text><xsl:value-of select="$north"/>],[<xsl:value-of select="$east"/><xsl:text>,</xsl:text><xsl:value-of select="$north"/>],[<xsl:value-of select="$east"/><xsl:text>,</xsl:text><xsl:value-of select="$south"/>],[<xsl:value-of select="$west"/><xsl:text>,</xsl:text><xsl:value-of select="$south"/>],[<xsl:value-of select="$west"/><xsl:text>,</xsl:text><xsl:value-of select="$north"/>]]]}</xsl:when>
        <xsl:when test="$polygon != ''">{"type":"Polygon","crs":{"type":"name","properties":{"name":"<xsl:value-of select="$SrsUrn"/>"}},"coordinates":[[[<xsl:value-of select="$polygonAsGeoJSON"/>]]]}</xsl:when>
      </xsl:choose>
    </xsl:param>
-->
<!-- Geolocation -->
    
    <xsl:if test="$place != '' or $point != '' or $box != '' or $polygon != ''">
      <dct:spatial>
        <dct:Location>
          <xsl:if test="$place != ''">
            <xsl:choose>
              <xsl:when test="normalize-space(*[local-name() = 'geoLocationPlace']/@xml:lang) != ''">
                <locn:geographicName xml:lang="{*[local-name() = 'geoLocationPlace']/@xml:lang}"><xsl:value-of select="$place"/></locn:geographicName>
              </xsl:when>
              <xsl:otherwise>
                <locn:geographicName><xsl:value-of select="$place"/></locn:geographicName>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:if>
          <xsl:if test="$point != ''">
            <geo:lat_long rdf:datatype="{$xsd}decimal"><xsl:value-of select="$point"/></geo:lat_long>
            <locn:geometry rdf:datatype="{$gsp}wktLiteral"><xsl:value-of select="$pointAsWKTLiteral"/></locn:geometry>
            <locn:geometry rdf:datatype="{$gsp}gmlLiteral"><xsl:value-of select="$pointAsGMLLiteral"/></locn:geometry>
            <locn:geometry rdf:datatype="{$geojsonMediaTypeUri}"><xsl:value-of select="$pointAsGeoJSONLiteral"/></locn:geometry>
          </xsl:if>
          <xsl:if test="$box != ''">
            <schema:box rdf:datatype="{$xsd}string"><xsl:value-of select="$box"/></schema:box>
            <locn:geometry rdf:datatype="{$gsp}wktLiteral"><xsl:value-of select="$boxAsWKTLiteral"/></locn:geometry>
            <locn:geometry rdf:datatype="{$gsp}gmlLiteral"><xsl:value-of select="$boxAsGMLLiteral"/></locn:geometry>
            <locn:geometry rdf:datatype="{$geojsonMediaTypeUri}"><xsl:value-of select="$boxAsGeoJSONLiteral"/></locn:geometry>
          </xsl:if>
          <xsl:if test="$polygon != ''">
            <schema:polygon><xsl:value-of select="normalize-space(translate($polygonAsLatLon,',',' '))"/></schema:polygon>
            <locn:geometry rdf:datatype="{$gsp}wktLiteral"><xsl:value-of select="$polygonAsWKTLiteral"/></locn:geometry>
            <locn:geometry rdf:datatype="{$gsp}gmlLiteral"><xsl:value-of select="$polygonAsGMLLiteral"/></locn:geometry>
            <locn:geometry rdf:datatype="{$geojsonMediaTypeUri}"><xsl:value-of select="$polygonAsGeoJSONLiteral"/></locn:geometry>
          </xsl:if>
        </dct:Location>
      </dct:spatial>
    </xsl:if>
    
  </xsl:template>

<!-- Sizes template -->

  <xsl:template name="Size" match="*[local-name() = 'sizes']/*[local-name() = 'size']">
<!--  
    <dcat:byteSize rdf:datatype="{$xsd}decimal"><xsl:value-of select="normalize-space(.)"/></dcat:byteSize>
-->
    <xsl:if test="$profile = 'extended'">
      <dct:extent>
        <dct:SizeOrDuration>
          <xsl:choose>
            <xsl:when test="normalize-space(@xml:lang) != ''">
              <rdfs:label xml:lang="{@xml:lang}"><xsl:value-of select="normalize-space(.)"/></rdfs:label>
            </xsl:when>
            <xsl:otherwise>
              <rdfs:label><xsl:value-of select="normalize-space(.)"/></rdfs:label>
            </xsl:otherwise>
          </xsl:choose>
        </dct:SizeOrDuration>
      </dct:extent>    
    </xsl:if>
  </xsl:template>

<!-- Dates template -->

  <xsl:template name="PublicationYear" match="*[local-name() = 'publicationYear']">
    <dct:issued rdf:datatype="{$xsd}gYear">
      <xsl:value-of select="normalize-space(.)"/>
    </dct:issued>
  </xsl:template>

  <xsl:template name="Dates" match="*[local-name() = 'dates']/*[local-name() = 'date']">
    <xsl:variable name="date" select="normalize-space(.)"/>
    <xsl:variable name="type" select="normalize-space(translate(@dateType,$uppercase,$lowercase))"/>
    <xsl:variable name="dateDataType">
      <xsl:choose>
        <xsl:when test="string-length($date) = 4">
          <xsl:text>gYear</xsl:text>
        </xsl:when>
        <xsl:when test="string-length($date) = 10">
          <xsl:text>date</xsl:text>
        </xsl:when>
        <xsl:when test="string-length($date) &gt; 10">
          <xsl:text>dateTime</xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>date</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
<!-- Added in DataCite v4.1 -->
<!-- NB: Currently not mapped. Options could be to use reification or PROV-O -->
    <xsl:variable name="dateInformation" select="normalize-space(@dateInformation)"/>
    <xsl:choose>
      <xsl:when test="$type = 'issued'">
        <dct:issued rdf:datatype="{$xsd}{$dateDataType}">
          <xsl:value-of select="$date"/>
        </dct:issued>
      </xsl:when>
      <xsl:when test="$type = 'updated'">
        <dct:modified rdf:datatype="{$xsd}{$dateDataType}">
          <xsl:value-of select="$date"/>
        </dct:modified>
      </xsl:when>
      <xsl:when test="$type = 'created' and $profile = 'extended'">
        <dct:created rdf:datatype="{$xsd}{$dateDataType}">
          <xsl:value-of select="$date"/>
        </dct:created>
      </xsl:when> 
      <xsl:when test="$type = 'accepted' and $profile = 'extended'">
        <dct:dateAccepted rdf:datatype="{$xsd}{$dateDataType}">
          <xsl:value-of select="$date"/>
        </dct:dateAccepted>
      </xsl:when>
      <xsl:when test="$type = 'available' and $profile = 'extended'">
        <dct:available rdf:datatype="{$xsd}{$dateDataType}">
          <xsl:value-of select="$date"/>
        </dct:available>
      </xsl:when>
      <xsl:when test="$type = 'copyrighted' and $profile = 'extended'">
        <dct:dateCopyrighted rdf:datatype="{$xsd}{$dateDataType}">
          <xsl:value-of select="$date"/>
        </dct:dateCopyrighted>
      </xsl:when>
      <xsl:when test="$type = 'collected' and $profile = 'extended'">
        <dct:created rdf:datatype="{$xsd}{$dateDataType}">
          <xsl:value-of select="$date"/>
        </dct:created>
      </xsl:when>
      <xsl:when test="$type = 'submitted' and $profile = 'extended'">
        <dct:dateSubmitted rdf:datatype="{$xsd}{$dateDataType}">
          <xsl:value-of select="$date"/>
        </dct:dateSubmitted>
      </xsl:when>
      <xsl:when test="$type = 'valid' and $profile = 'extended'">
        <dct:valid rdf:datatype="{$xsd}{$dateDataType}">
          <xsl:value-of select="$date"/>
        </dct:valid>
      </xsl:when>
<!-- Added in DataCite v4.1 -->
      <xsl:when test="$type = 'other'">
        <dct:date rdf:datatype="{$xsd}{$dateDataType}">
          <xsl:value-of select="$date"/>
        </dct:date>
      </xsl:when>
<!-- Added in DataCite v4.2 -->
      <xsl:when test="$type = 'withdrawn' and $profile = 'extended'">
        <dct:modified rdf:datatype="{$xsd}{$dateDataType}">
          <xsl:value-of select="$date"/>
        </dct:modified>
        <adms:status rdf:resource="{$opds}WITHDRAWN"/>
      </xsl:when>
      <xsl:otherwise>
        <dct:date rdf:datatype="{$xsd}{$dateDataType}">
          <xsl:value-of select="$date"/>
        </dct:date>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

<!-- Publisher template -->

  <xsl:template name="Publisher" match="*[local-name() = 'publisher']">
    <dct:publisher>
      <foaf:Agent>
        <foaf:name><xsl:value-of select="normalize-space(.)"/></foaf:name>
      </foaf:Agent>
    </dct:publisher>
  </xsl:template>
  
<!-- Creators and contributors template -->

  <xsl:template name="Agents" match="*[local-name() = 'creators']/*[local-name() = 'creator']|*[local-name() = 'contributors']/*[local-name() = 'contributor']">
<!-- Added in DataCite v4.1 -->
    <xsl:param name="nameType">
      <xsl:choose>
        <xsl:when test="local-name(.) = 'creator' and *[local-name() = 'creatorName']/@nameType">
          <xsl:value-of select="translate(normalize-space(*[local-name() = 'creatorName']/@nameType),$uppercase,$lowercase)"/>
        </xsl:when>
        <xsl:when test="local-name(.) = 'contributor' and *[local-name() = 'contributorName']/@nameType">
          <xsl:value-of select="translate(normalize-space(*[local-name() = 'contributorName']/@nameType),$uppercase,$lowercase)"/>
        </xsl:when>
      </xsl:choose>
    </xsl:param>
    <xsl:param name="agentName">
      <xsl:choose>
        <xsl:when test="local-name(.) = 'creator'">
          <xsl:value-of select="normalize-space(*[local-name() = 'creatorName'])"/>
        </xsl:when>
        <xsl:when test="local-name(.) = 'contributor'">
          <xsl:value-of select="normalize-space(*[local-name() = 'contributorName'])"/>
        </xsl:when>
      </xsl:choose>
    </xsl:param>
    <xsl:param name="agentFamilyName">
      <xsl:choose>
<!-- Added in DataCite v4.0 -->
        <xsl:when test="*[local-name() = 'familyName']">
          <xsl:value-of select="normalize-space(*[local-name() = 'familyName'])"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="normalize-space(substring-before($agentName, ','))"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:param>
    <xsl:param name="agentGivenName">
      <xsl:choose>
<!-- Added in DataCite v4.0 -->
        <xsl:when test="*[local-name() = 'givenName']">
          <xsl:value-of select="normalize-space(*[local-name() = 'givenName'])"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="normalize-space(substring-after($agentName, ','))"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:param>
    <xsl:param name="type" select="normalize-space(translate(@contributorType,$uppercase,$lowercase))"/>
    <xsl:param name="nameIdentifier" select="normalize-space(*[local-name() = 'nameIdentifier'])"/>
    <xsl:param name="nameIdentifierScheme" select="normalize-space(translate(*[local-name() = 'nameIdentifier']/@nameIdentifierScheme,$uppercase,$lowercase))"/>
    <xsl:param name="schemeURI" select="normalize-space(translate(*[local-name() = 'nameIdentifier']/@schemeURI,$uppercase,$lowercase))"/>
    <xsl:param name="uri">
      <xsl:call-template name="IdentifierURI">
        <xsl:with-param name="identifier" select="$nameIdentifier"/>
        <xsl:with-param name="type" select="$nameIdentifierScheme"/>
        <xsl:with-param name="schemeURI" select="$schemeURI"/>
      </xsl:call-template>
    </xsl:param>    
    <xsl:param name="nameIdentifierDatatype">
      <xsl:choose>
        <xsl:when test="starts-with(translate(normalize-space($nameIdentifier),$uppercase,$lowercase),'http://')">
          <xsl:value-of select="concat($xsd,'anyURI')"/>
        </xsl:when>
        <xsl:when test="starts-with(translate(normalize-space($nameIdentifier),$uppercase,$lowercase),'https://')">
          <xsl:value-of select="concat($xsd,'anyURI')"/>
        </xsl:when>
        <xsl:when test="starts-with(translate(normalize-space($nameIdentifier),$uppercase,$lowercase),'urn://')">
          <xsl:value-of select="concat($xsd,'anyURI')"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="concat($xsd,'string')"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:param>
    <xsl:param name="agentType">
      <xsl:choose>
        <xsl:when test="$type = 'contactperson'">
          <xsl:choose>
            <xsl:when test="$nameType = 'personal'">
              <rdf:type rdf:resource="{$vcard}Individual"/>
            </xsl:when>
            <xsl:when test="$nameType = 'organizational'">
              <rdf:type rdf:resource="{$vcard}Organization"/>
            </xsl:when>
            <xsl:otherwise>
              <rdf:type rdf:resource="{$vcard}Individual"/>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:when>
        <xsl:otherwise>
          <xsl:choose>
            <xsl:when test="$nameType = 'personal'">
              <rdf:type rdf:resource="{$foaf}Person"/>
            </xsl:when>
            <xsl:when test="$nameType = 'organizational'">
              <rdf:type rdf:resource="{$foaf}Organization"/>
            </xsl:when>
            <xsl:otherwise>
              <rdf:type rdf:resource="{$foaf}Agent"/>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:param>
    <xsl:param name="agentDescription">
      <xsl:copy-of select="$agentType"/>
      <xsl:if test="$nameIdentifier != ''">
        <dct:identifier rdf:datatype="{$nameIdentifierDatatype}"><xsl:value-of select="$nameIdentifier"/></dct:identifier>
      </xsl:if>
      <xsl:choose>
        <xsl:when test="$type = 'contactperson'">
<!--        
          <rdf:type rdf:resource="{$vcard}Individual"/>
-->
          <xsl:if test="$agentName != ''">
            <vcard:fn><xsl:value-of select="$agentName"/></vcard:fn>
            <vcard:given-name><xsl:value-of select="$agentGivenName"/></vcard:given-name>
            <vcard:family-name><xsl:value-of select="$agentFamilyName"/></vcard:family-name>
          </xsl:if>
          <xsl:for-each select="*[local-name() = 'affiliation']">
            <vcard:organization-name><xsl:value-of select="."/></vcard:organization-name>
          </xsl:for-each>
        </xsl:when>
        <xsl:otherwise>
<!--        
          <rdf:type rdf:resource="{$foaf}Agent"/>
-->
          <xsl:if test="$agentName != ''">
            <foaf:name><xsl:value-of select="$agentName"/></foaf:name>
          </xsl:if>
          <xsl:if test="$agentGivenName != ''">
            <foaf:givenName><xsl:value-of select="$agentGivenName"/></foaf:givenName>
          </xsl:if>
          <xsl:if test="$agentFamilyName != ''">
            <foaf:familyName><xsl:value-of select="$agentFamilyName"/></foaf:familyName>
          </xsl:if>
          <xsl:for-each select="*[local-name() = 'affiliation']">
            <org:memberOf>
              <xsl:call-template name="Affiliations"/>
            </org:memberOf>
          </xsl:for-each>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:param>
    <xsl:param name="agent">
      <xsl:variable name="urilc" select="translate($uri,$uppercase,$lowercase)"/>
      <xsl:choose>
        <xsl:when test="$uri != '' and ( starts-with($urilc, 'http://') or starts-with($urilc, 'https://') or starts-with($urilc, 'urn://') )">
          <rdf:Description rdf:about="{$uri}">
            <xsl:copy-of select="$agentDescription"/>
          </rdf:Description>
        </xsl:when>
        <xsl:otherwise>
          <rdf:Description>
            <xsl:if test="$uri != ''">
              <dct:identifier rdf:datatype="{$xsd}string"><xsl:value-of select="$uri"/></dct:identifier>
            </xsl:if>
            <xsl:copy-of select="$agentDescription"/>
          </rdf:Description>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:param>
    <xsl:choose>
      <xsl:when test="local-name(.) = 'creator' and $profile = 'extended'">
        <dct:creator><xsl:copy-of select="$agent"/></dct:creator>
      </xsl:when>
      <xsl:when test="local-name(.) = 'contributor'">
        <xsl:choose>
          <xsl:when test="$type = 'contactperson'">
            <dcat:contactPoint><xsl:copy-of select="$agent"/></dcat:contactPoint>
          </xsl:when>
          <xsl:when test="$profile = 'extended'">
            <xsl:choose>
<!-- TBD -->
<!--
              <xsl:when test="$type = 'datacollector'">
                <dct:contributor><xsl:copy-of select="$agent"/></dct:contributor>
              </xsl:when>
-->
<!-- TBD -->
<!--
              <xsl:when test="$type = 'datacurator'">
                <dct:contributor><xsl:copy-of select="$agent"/></dct:contributor>
              </xsl:when>
-->
<!-- TBD -->
<!--
              <xsl:when test="$type = 'datamanager'">
                <dct:contributor><xsl:copy-of select="$agent"/></dct:contributor>
              </xsl:when>
-->
<!-- Mapping to be confirmed when the final version of DUV will be realeased -->

              <xsl:when test="$type = 'distributor'">
                <duv:hasDistributor><xsl:copy-of select="$agent"/></duv:hasDistributor>
              </xsl:when>
              
              <xsl:when test="$type = 'editor'">
                <schema:editor><xsl:copy-of select="$agent"/></schema:editor>
              </xsl:when>
<!-- Unstable -->
              <xsl:when test="$type = 'funder'">
                <schema:funder><xsl:copy-of select="$agent"/></schema:funder>
              </xsl:when>
<!-- TBD -->
<!--
              <xsl:when test="$type = 'hostinginstitution'">
                <dct:contributor><xsl:copy-of select="$agent"/></dct:contributor>
              </xsl:when>
              <xsl:when test="$type = 'producer'">
                <schema:producer><xsl:copy-of select="$agent"/></schema:producer>
              </xsl:when>
-->
<!-- TBD -->
<!--
              <xsl:when test="$type = 'projectleader'">
                <dct:contributor><xsl:copy-of select="$agent"/></dct:contributor>
                <prov:wasGeneratedBy>
                  <foaf:Project>
                    <??:??><xsl:copy-of select="$agent"/></??:??>
                  </foaf:Project>
                </prov:wasGeneratedBy>
              </xsl:when>
-->
<!-- TBD -->
<!--
              <xsl:when test="$type = 'projectmanager'">
                <dct:contributor><xsl:copy-of select="$agent"/></dct:contributor>
                <prov:wasGeneratedBy>
                  <foaf:Project>
                    <??:??><xsl:copy-of select="$agent"/></??:??>
                  </foaf:Project>
                </prov:wasGeneratedBy>
              </xsl:when>
-->
<!-- TBD -->
              <xsl:when test="$type = 'projectmember'">
                <dct:contributor><xsl:copy-of select="$agent"/></dct:contributor>
                <prov:wasGeneratedBy>
                  <foaf:Project>
                    <foaf:member><xsl:copy-of select="$agent"/></foaf:member>
                  </foaf:Project>
                </prov:wasGeneratedBy>
              </xsl:when>
<!-- TBD -->
<!--
              <xsl:when test="$type = 'registrationagency'">
                <dct:contributor><xsl:copy-of select="$agent"/></dct:contributor>
              </xsl:when>
-->
<!-- TBD -->
<!--
              <xsl:when test="$type = 'registrationauthority'">
                <dct:contributor><xsl:copy-of select="$agent"/></dct:contributor>
              </xsl:when>
-->
<!-- TBD -->
<!--
              <xsl:when test="$type = 'relatedperson'">
                <dct:contributor><xsl:copy-of select="$agent"/></dct:contributor>
              </xsl:when>
-->
<!-- TBD -->
<!--
              <xsl:when test="$type = 'researcher'">
                <dct:contributor><xsl:copy-of select="$agent"/></dct:contributor>
              </xsl:when>
-->
<!-- TBD -->
<!--
              <xsl:when test="$type = 'researchgroup'">
                <dct:contributor><xsl:copy-of select="$agent"/></dct:contributor>
              </xsl:when>
-->
<!-- TBD -->
              <xsl:when test="$type = 'rightsholder'">
                <dct:rightsHolder><xsl:copy-of select="$agent"/></dct:rightsHolder>
              </xsl:when>
<!-- Unstable -->
              <xsl:when test="$type = 'sponsor'">
                <schema:sponsor><xsl:copy-of select="$agent"/></schema:sponsor>
              </xsl:when> 
<!-- TBD -->
<!--
              <xsl:when test="$type = 'supervisor'">
                <dct:contributor><xsl:copy-of select="$agent"/></dct:contributor>
              </xsl:when>
-->
<!-- TBD -->
<!--
              <xsl:when test="$type = 'workpackageleader'">
                <dct:contributor><xsl:copy-of select="$agent"/></dct:contributor>
              </xsl:when>
-->
<!-- TBD -->
              <xsl:when test="$type = 'other'">
                <dct:contributor><xsl:copy-of select="$agent"/></dct:contributor>
              </xsl:when>
              <xsl:otherwise>
                <dct:contributor><xsl:copy-of select="$agent"/></dct:contributor>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:when>
<!-- Default mapping of contributor types not support in the core profile -->
<!--
          <xsl:otherwise>
            <dct:contributor><xsl:copy-of select="$agent"/></dct:contributor>
          </xsl:otherwise>
-->
        </xsl:choose>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

<!-- Main and alternate identifiers template -->

  <xsl:template name="Identifiers" match="*[local-name() = 'identifier']|*[local-name() = 'alternateIdentifiers']/*[local-name() = 'alternateIdentifier']">
    <xsl:param name="ResourceType"/>
    <xsl:param name="identifier" select="normalize-space(.)"/>
    <xsl:param name="type-original">
      <xsl:choose>
        <xsl:when test="local-name() = 'identifier'">
          <xsl:value-of select="normalize-space(@identifierType)"/>
        </xsl:when>
        <xsl:when test="local-name() = 'alternateIdentifier'">
          <xsl:value-of select="normalize-space(@alternateIdentifierType)"/>
        </xsl:when>
      </xsl:choose>
    </xsl:param>
    <xsl:param name="type" select="translate($type-original,$uppercase,$lowercase)"/>
    <xsl:param name="schemeURI" select="@schemeURI"/>
    <xsl:param name="uri">
      <xsl:call-template name="IdentifierURI">
        <xsl:with-param name="identifier" select="$identifier"/>
        <xsl:with-param name="type" select="$type"/>
        <xsl:with-param name="schemeURI" select="$schemeURI"/>
      </xsl:call-template>
    </xsl:param>    
    <xsl:variable name="urilc" select="translate($uri,$uppercase,$lowercase)"/>
    <xsl:choose>
      <xsl:when test="$uri != '' and ( starts-with($urilc, 'http://') or starts-with($urilc, 'https://') or starts-with($urilc, 'urn:') )">
        <xsl:choose>
          <xsl:when test="local-name() = 'identifier'">
            <dct:identifier rdf:datatype="{$xsd}anyURI"><xsl:value-of select="$uri"/></dct:identifier>
            <xsl:choose>
              <xsl:when test="$ResourceType = dataset">
                <dcat:landingPage rdf:resource="{$uri}"/>
              </xsl:when>
              <xsl:otherwise>
                <foaf:page rdf:resource="{$uri}"/>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:when>
          <xsl:when test="local-name() = 'alternateIdentifier'">
            <owl:sameAs rdf:resource="{$uri}"/>
<!--            
            <adms:identifier rdf:resource="{$uri}"/>
-->
            <adms:identifier>
              <adms:Identifier>
                <skos:notation rdf:datatype="{$xsd}anyURI"><xsl:value-of select="$uri"/></skos:notation>
		<xsl:choose>
		  <xsl:when test="$type != ''">
		    <adms:schemeAgency><xsl:value-of select="$type-original"/></adms:schemeAgency>
		  </xsl:when>
		  <xsl:when test="$schemeURI != ''">
		    <dct:creator rdf:resource="{$schemeURI}"/>
		  </xsl:when>
		</xsl:choose>
              </adms:Identifier>
            </adms:identifier>
          </xsl:when>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <xsl:choose>
          <xsl:when test="local-name() = 'identifier'">
            <dc:identifier rdf:datatype="{$xsd}string"><xsl:value-of select="$uri"/></dc:identifier>
          </xsl:when>
          <xsl:when test="local-name() = 'alternateIdentifier'">
            <adms:identifier>
              <adms:Identifier>
                <skos:notation><xsl:value-of select="$uri"/></skos:notation>
		<xsl:choose>
		  <xsl:when test="$type != ''">
		    <adms:schemeAgency><xsl:value-of select="$type-original"/></adms:schemeAgency>
		  </xsl:when>
		  <xsl:when test="$schemeURI != ''">
		    <dct:creator rdf:resource="{$schemeURI}"/>
		  </xsl:when>
		</xsl:choose>
              </adms:Identifier>
            </adms:identifier>
          </xsl:when>
        </xsl:choose>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>    
  
<!-- Related identifiers template -->

  <xsl:template name="RelatedIdentifiers" match="*[local-name() = 'relatedIdentifiers']/*[local-name() = 'relatedIdentifier']">
    <xsl:param name="relation" select="normalize-space(translate(@relationType,$uppercase,$lowercase))"/>
    <xsl:param name="identifier" select="normalize-space(.)"/>
    <xsl:param name="type" select="normalize-space(translate(@relatedIdentifierType,$uppercase,$lowercase))"/>
    <xsl:param name="schemeURI" select="@schemeURI"/>
    <xsl:param name="uri">
      <xsl:call-template name="IdentifierURI">
        <xsl:with-param name="identifier" select="$identifier"/>
        <xsl:with-param name="type" select="$type"/>
        <xsl:with-param name="schemeURI" select="$schemeURI"/>
      </xsl:call-template>
    </xsl:param>    
<!-- Added in DataCite v4.1 -->
<!-- NB: Currently not mapped. -->
    <xsl:param name="resourceType" select="normalize-space(translate(@resourceTypeGeneral,$uppercase,$lowercase))"/>
    <xsl:choose>
      <xsl:when test="$relation = 'hasmetadata'">
        <foaf:isPrimaryTopicOf>
          <dcat:CatalogRecord rdf:about="{$uri}">
            <xsl:if test="@relatedMetadataScheme != '' or @schemeURI != ''">
              <xsl:choose>
                <xsl:when test="@relatedMetadataScheme != '' and @schemeURI != ''">
                  <dct:conformsTo>
                    <dct:Standard rdf:about="{@schemeURI}">
                      <dct:title><xsl:value-of select="normalize-space(@relatedMetadataScheme)"/></dct:title>
                    </dct:Standard>
                  </dct:conformsTo>
                </xsl:when>
                <xsl:when test="@relatedMetadataScheme != '' and not(@schemeURI != '')">
                  <dct:conformsTo>
                    <dct:Standard>
                      <dct:title><xsl:value-of select="normalize-space(@relatedMetadataScheme)"/></dct:title>
                    </dct:Standard>
                  </dct:conformsTo>
                </xsl:when>
                <xsl:when test="not(@relatedMetadataScheme != '') and @schemeURI != ''">
                  <dct:conformsTo>
                    <dct:Standard rdf:about="{@schemeURI}"/>
                  </dct:conformsTo>
                </xsl:when>
              </xsl:choose>
            </xsl:if>
          </dcat:CatalogRecord>
        </foaf:isPrimaryTopicOf>
      </xsl:when>
      <xsl:when test="$relation = 'isnewversionof'">
        <dct:isVersionOf rdf:resource="{$uri}"/>
      </xsl:when>
      <xsl:when test="$relation = 'ispreviousversionof'">
        <dct:hasVersion rdf:resource="{$uri}"/>
      </xsl:when>
      <xsl:when test="$relation = 'isdocumentedby'">
        <foaf:page rdf:resource="{$uri}"/>
      </xsl:when>
      <xsl:when test="$relation = 'isderivedfrom'">
        <dct:source rdf:resource="{$uri}"/>
      </xsl:when>
<!-- Added in DataCite v4.1 -->
      <xsl:when test="$relation = 'hasversion'">
        <dct:hasVersion rdf:resource="{$uri}"/>
      </xsl:when>
      <xsl:when test="$relation = 'isversionof'">
        <dct:isVersionOf rdf:resource="{$uri}"/>
      </xsl:when>
      <xsl:when test="$profile = 'extended'">
        <xsl:choose>
<!-- TBD -->
<!--
          <xsl:when test="$relation = 'iscitedby'">
            <dct:relation rdf:resource="{$uri}"/>
          </xsl:when>
-->
<!-- TBD -->
<!--
          <xsl:when test="$relation = 'cites'">
            <dct:relation rdf:resource="{$uri}"/>
          </xsl:when>
-->
<!-- TBD -->
<!--
          <xsl:when test="$relation = 'issupplementto'">
            <dct:relation rdf:resource="{$uri}"/>
          </xsl:when>
-->
<!-- TBD -->
<!--
          <xsl:when test="$relation = 'issupplementedby'">
            <dct:relation rdf:resource="{$uri}"/>
          </xsl:when>
-->
<!-- TBD -->
<!--
          <xsl:when test="$relation = 'iscontinuedby'">
            <dct:relation rdf:resource="{$uri}"/>
          </xsl:when>
-->
<!-- TBD -->
<!--
          <xsl:when test="$relation = 'continues'">
            <dct:relation rdf:resource="{$uri}"/>
          </xsl:when>
-->
          <xsl:when test="$relation = 'ismetadatafor'">
            <foaf:primaryTopic rdf:resource="{$uri}"/>
          </xsl:when>
          <xsl:when test="$relation = 'ispartof'">
            <dct:isPartOf rdf:resource="{$uri}"/>
          </xsl:when>
          <xsl:when test="$relation = 'haspart'">
            <dct:hasPart rdf:resource="{$uri}"/>
          </xsl:when>
          <xsl:when test="$relation = 'isreferencedby'">
            <dct:isReferencedBy rdf:resource="{$uri}"/>
          </xsl:when>
          <xsl:when test="$relation = 'references'">
            <dct:references rdf:resource="{$uri}"/>
          </xsl:when>
<!-- TBD -->
<!--
          <xsl:when test="$relation = 'documents'">
            <dct:relation rdf:resource="{$uri}"/>
          </xsl:when>
-->
<!-- TBD -->
<!--
          <xsl:when test="$relation = 'iscompiledby'">
            <dct:relation rdf:resource="{$uri}"/>
          </xsl:when>
-->
<!-- TBD -->
<!--
          <xsl:when test="$relation = 'compiles'">
            <dct:relation rdf:resource="{$uri}"/>
          </xsl:when>
-->
          <xsl:when test="$relation = 'isvariantformof'">
            <schema:isVariantOf rdf:resource="{$uri}"/>
          </xsl:when>
<!-- TBD -->
<!--
          <xsl:when test="$relation = 'isoriginalformof'">
            <dct:relation rdf:resource="{$uri}"/>
          </xsl:when>
-->
          <xsl:when test="$relation = 'isidenticalto'">
            <owl:sameAs rdf:resource="{$uri}"/>
          </xsl:when>
          <xsl:when test="$relation = 'isreviewedby'">
            <schema:review rdf:resource="{$uri}"/>
          </xsl:when>
          <xsl:when test="$relation = 'reviews'">
            <schema:itemReviewed rdf:resource="{$uri}"/>
          </xsl:when>
          <xsl:when test="$relation = 'issourceof'">
            <prov:hadDerivation rdf:resource="{$uri}"/>
          </xsl:when>
<!-- Added in DataCite v4.1 -->
<!-- TBD -->
<!--
          <xsl:when test="$relation = 'describes'">
            <dct:relation rdf:resource="{$uri}"/>
          </xsl:when>
-->
<!-- Added in DataCite v4.1 -->
          <xsl:when test="$relation = 'isdescribedby'">
            <wdrs:describedby rdf:resource="{$uri}"/>
          </xsl:when>
          <xsl:when test="$relation = 'requires'">
            <dct:requires rdf:resource="{$uri}"/>
          </xsl:when>
          <xsl:when test="$relation = 'isrequiredby'">
            <dct:isRequiredBy rdf:resource="{$uri}"/>
          </xsl:when>
<!-- Added in DataCite v4.2 -->
          <xsl:when test="$relation = 'obsoletes'">
            <dct:replaces rdf:resource="{$uri}"/>
          </xsl:when>
<!-- Added in DataCite v4.2 -->
          <xsl:when test="$relation = 'isobsoletedby'">
            <dct:isReplacedBy rdf:resource="{$uri}"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:variable name="urilc" select="translate($uri,$uppercase,$lowercase)"/>
            <xsl:choose>
              <xsl:when test="$uri != '' and ( starts-with($urilc, 'http://') or starts-with($urilc, 'https://') or starts-with($urilc, 'urn://') )">
                <dct:relation rdf:resource="{$uri}"/>
              </xsl:when>
              <xsl:otherwise>
                <dct:relation rdf:parseType="Resource">
                  <dc:identifier><xsl:value-of select="$uri"/></dc:identifier>
                </dct:relation>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <xsl:variable name="urilc" select="translate($uri,$uppercase,$lowercase)"/>
        <xsl:choose>
          <xsl:when test="$uri != '' and ( starts-with($urilc, 'http://') or starts-with($urilc, 'https://') or starts-with($urilc, 'urn://') )">
            <dct:relation rdf:resource="{$uri}"/>
          </xsl:when>
          <xsl:otherwise>
            <dct:relation rdf:parseType="Resource">
              <dc:identifier><xsl:value-of select="$uri"/></dc:identifier>
            </dct:relation>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>    

<!-- Formats template -->

  <xsl:template name="Formats" match="*[local-name() = 'formats']/*[local-name() = 'format']">
    <xsl:variable name="format" select="normalize-space(.)"/>
    <xsl:variable name="type" select="substring-before($format,'/')"/>
    <xsl:choose>
      <xsl:when test="$type = 'text' or $type = 'image' or $type = 'audio' or $type = 'video' or $type = 'application' or $type = 'multipart' or $type = 'message'">
        <dcat:mediaType rdf:resource="{$ianaMT}{$format}"/>
      </xsl:when>
      <xsl:otherwise>
        <dct:format>
          <dct:MediaTypeOrExtent>
            <rdfs:label><xsl:value-of select="$format"/></rdfs:label>
          </dct:MediaTypeOrExtent>
        </dct:format>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
<!-- Language template -->

  <xsl:template name="Language" match="*[local-name() = 'language']">
    <xsl:variable name="langCodeAlpha3">
      <xsl:call-template name="LanguageAlpha3">
        <xsl:with-param name="langCode" select="normalize-space(.)"/>
      </xsl:call-template>
    </xsl:variable>
    <dct:language rdf:resource="{$oplang}{translate($langCodeAlpha3,$lowercase,$uppercase)}"/>
  </xsl:template>

<!-- Resource type template -->
    
  <xsl:template name="ResourceType" match="*[local-name() = 'resourceType']">
    <xsl:param name="type" select="normalize-space(translate(@resourceTypeGeneral,$uppercase,$lowercase))"/>
    <xsl:choose>
      <xsl:when test="$type = 'audiovisual'">
        <rdf:type rdf:resource="{$dcat}Dataset"/>
        <xsl:if test="$profile = 'extended'">
          <dct:type rdf:resource="{$dctype}MovingImage"/>
        </xsl:if>
      </xsl:when>
      <xsl:when test="$type = 'collection'">
        <rdf:type rdf:resource="{$dcat}Dataset"/>
        <xsl:if test="$profile = 'extended'">
          <dct:type rdf:resource="{$dctype}Collection"/>
        </xsl:if>
      </xsl:when>
<!-- Added in DataCite v4.1 -->
      <xsl:when test="$type = 'datapaper'">
        <rdf:type rdf:resource="{$dcat}Dataset"/>
        <xsl:if test="$profile = 'extended'">
<!-- TBD -->
<!--        
          <dct:type rdf:resource="{$dctype}??"/>
-->
        </xsl:if>
      </xsl:when>
      <xsl:when test="$type = 'dataset'">
        <rdf:type rdf:resource="{$dcat}Dataset"/>
        <xsl:if test="$profile = 'extended'">
          <dct:type rdf:resource="{$dctype}Dataset"/>
        </xsl:if>
      </xsl:when>
      <xsl:when test="$type = 'event'">
        <xsl:if test="$profile = 'extended'">
          <rdf:type rdf:resource="{$dctype}Event"/>
          <dct:type rdf:resource="{$dctype}Event"/>
        </xsl:if>
      </xsl:when>
      <xsl:when test="$type = 'image'">
        <rdf:type rdf:resource="{$dcat}Dataset"/>
        <xsl:if test="$profile = 'extended'">
          <dct:type rdf:resource="{$dctype}Image"/>
        </xsl:if>
      </xsl:when>
      <xsl:when test="$type = 'interactiveresource'">
        <rdf:type rdf:resource="{$dcat}Dataset"/>
        <xsl:if test="$profile = 'extended'">
          <dct:type rdf:resource="{$dctype}InteractiveResource"/>
        </xsl:if>
      </xsl:when>
      <xsl:when test="$type = 'model'">
        <rdf:type rdf:resource="{$dcat}Dataset"/>
        <xsl:if test="$profile = 'extended'">
<!-- TBD -->
<!--        
          <dct:type rdf:resource="{$dctype}??"/>
-->
        </xsl:if>
      </xsl:when>
      <xsl:when test="$type = 'physicalobject'">
        <xsl:if test="$profile = 'extended'">
          <rdf:type rdf:resource="{$dctype}PhysicalObject"/>
          <dct:type rdf:resource="{$dctype}PhysicalObject"/>
        </xsl:if>
      </xsl:when>
      <xsl:when test="$type = 'service'">
        <xsl:if test="$profile = 'extended'">
          <rdf:type rdf:resource="{$dctype}Service"/>
          <dct:type rdf:resource="{$dctype}Service"/>
        </xsl:if>
      </xsl:when>
      <xsl:when test="$type = 'software'">
        <rdf:type rdf:resource="{$dcat}Dataset"/>
        <xsl:if test="$profile = 'extended'">
          <dct:type rdf:resource="{$dctype}Software"/>
        </xsl:if>
      </xsl:when>
      <xsl:when test="$type = 'sound'">
        <rdf:type rdf:resource="{$dcat}Dataset"/>
        <xsl:if test="$profile = 'extended'">
          <dct:type rdf:resource="{$dctype}Sound"/>
        </xsl:if>
      </xsl:when>
      <xsl:when test="$type = 'text'">
        <rdf:type rdf:resource="{$dcat}Dataset"/>
        <xsl:if test="$profile = 'extended'">
          <dct:type rdf:resource="{$dctype}Text"/>
        </xsl:if>
      </xsl:when>
      <xsl:when test="$type = 'workflow'">
        <rdf:type rdf:resource="{$dcat}Dataset"/>
        <xsl:if test="$profile = 'extended'">
<!-- TBD -->
<!--        
          <dct:type rdf:resource="{$dctype}??"/>
-->
        </xsl:if>
      </xsl:when>
      <xsl:when test="$type = 'other'">
<!-- TBD -->
<!--      
        <rdf:type rdf:resource="{$dctype}??"/>
-->
      </xsl:when>
      <xsl:otherwise>
<!-- TBD -->
<!--      
        <rdf:type rdf:resource="{$dctype}??"/>
-->
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

<!-- 

  Mapping templates     
  =================
 
 -->

<!-- Template for creating the absolute URI of an identifier -->

  <xsl:template name="IdentifierURI">
    <xsl:param name="identifier"/>
    <xsl:param name="type"/>
    <xsl:param name="schemeURI"/>
<!-- Resolvers -->
    <xsl:variable name="orcid">http://orcid.org/</xsl:variable>
    <xsl:variable name="isni">http://www.isni.org/</xsl:variable>
    <xsl:variable name="grid">https://www.grid.ac/institutes/</xsl:variable>
<!--    
    <xsl:variable name="fundref">http://www.crossref.org/fundref/</xsl:variable>
    <xsl:variable name="fundref">https://doi.org/</xsl:variable>
-->
    <xsl:variable name="fundref"></xsl:variable>
<!-- Added in DataCite v4.3 -->
    <xsl:variable name="ror"></xsl:variable>
    <xsl:variable name="n2t">http://n2t.net/</xsl:variable>
    <xsl:variable name="arxiv">http://arxiv.org/abs/</xsl:variable>
    <xsl:variable name="doi">https://doi.org/</xsl:variable>
    <xsl:variable name="bibcode">http://adsabs.harvard.edu/abs/</xsl:variable>
    <xsl:variable name="pmid">http://www.ncbi.nlm.nih.gov/pubmed/</xsl:variable>
    <xsl:variable name="handle">https://hdl.handle.net/</xsl:variable>
<!-- Added in DataCite v4.0 -->
    <xsl:variable name="igsn">https://hdl.handle.net/10273/</xsl:variable>
    <xsl:variable name="istc">http://istc-search-beta.peppertag.com/ptproc/IstcSearch?tFrame=IstcListing&amp;tForceNewQuery=Yes&amp;esfIstc=</xsl:variable>
<!--    
    <xsl:variable name="issn">urn:issn:</xsl:variable>
-->
    <xsl:variable name="issn">http://issn.org/resource/ISSN/</xsl:variable>
    <xsl:variable name="lissn">http://issn.org/resource/ISSN-L/</xsl:variable>
    <xsl:variable name="isbn">urn:isbn:</xsl:variable>
    <xsl:choose>
      <xsl:when test="$type = 'orcid'">
        <xsl:value-of select="concat($orcid,$identifier)"/>
      </xsl:when>
      <xsl:when test="$type = 'isni'">
        <xsl:value-of select="concat($isni,$identifier)"/>
      </xsl:when>
      <xsl:when test="$type = 'grid'">
        <xsl:value-of select="concat($isni,$identifier)"/>
      </xsl:when>
      <xsl:when test="$type = 'crossref funder id'">
        <xsl:value-of select="concat($fundref,$identifier)"/>
      </xsl:when>
<!-- Added in DataCite v4.3 -->
      <xsl:when test="$type = 'ror'">
        <xsl:value-of select="concat($ror,$identifier)"/>
      </xsl:when>
      <xsl:when test="$type = 'ark'">
        <xsl:value-of select="concat($n2t,$identifier)"/>
      </xsl:when>
      <xsl:when test="$type = 'arxiv'">
        <xsl:value-of select="concat($arxiv,substring-after($identifier,':'))"/>
      </xsl:when>
      <xsl:when test="$type = 'bibcode'">
        <xsl:value-of select="concat($bibcode,$identifier)"/>
      </xsl:when>
      <xsl:when test="$type = 'doi'">
        <xsl:value-of select="concat($doi,$identifier)"/>
      </xsl:when>
      <xsl:when test="$type = 'ean13'">
<!-- To be fixed - fictional URN namespace -->
        <xsl:value-of select="concat('urn:ean-13:',$identifier)"/>
      </xsl:when>
      <xsl:when test="$type = 'eissn'">
        <xsl:value-of select="concat($issn,$identifier)"/>
      </xsl:when>
      <xsl:when test="$type = 'handle'">
        <xsl:value-of select="concat($handle,$identifier)"/>
      </xsl:when>
      <xsl:when test="$type = 'isbn'">
        <xsl:value-of select="concat($isbn,$identifier)"/>
      </xsl:when>
      <xsl:when test="$type = 'igsn'">
        <xsl:value-of select="concat($igsn,$identifier)"/>
      </xsl:when>
      <xsl:when test="$type = 'issn'">
        <xsl:value-of select="concat($issn,$identifier)"/>
      </xsl:when>
      <xsl:when test="$type = 'istc'">
        <xsl:value-of select="concat($istc,$identifier)"/>
      </xsl:when>
      <xsl:when test="$type = 'lissn'">
        <xsl:value-of select="concat($lissn,$identifier)"/>
      </xsl:when>
      <xsl:when test="$type = 'lsid'">
        <xsl:value-of select="$identifier"/>
      </xsl:when>
      <xsl:when test="$type = 'pmid'">
        <xsl:value-of select="concat($pmid,$identifier)"/>
      </xsl:when>
      <xsl:when test="$type = 'purl'">
        <xsl:value-of select="$identifier"/>
      </xsl:when>
      <xsl:when test="$type = 'upc'">
<!-- To be fixed - fictional URN namespace -->
        <xsl:value-of select="concat('urn:upc:',$identifier)"/>
      </xsl:when>
      <xsl:when test="$type = 'url'">
        <xsl:value-of select="$identifier"/>
      </xsl:when>
      <xsl:when test="$type = 'urn'">
        <xsl:value-of select="$identifier"/>
      </xsl:when>
<!-- Added in DataCite v4.2 -->
      <xsl:when test="$type = 'w3id'">
        <xsl:value-of select="$identifier"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$identifier"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

<!-- Affiliation template -->

  <xsl:template name="Affiliations">  
    <xsl:param name="affiliationIdentifier" select="normalize-space(@affiliationIdentifier)"/>
    <xsl:param name="affiliationIdentifierScheme" select="normalize-space(@affiliationIdentifierScheme)"/>
    <xsl:param name="affiliationSchemeURI" select="translate(normalize-space(@schemeURI),$uppercase,$lowercase)"/>
    <xsl:param name="affiliationURI">
      <xsl:variable name="uri">
        <xsl:call-template name="IdentifierURI">
          <xsl:with-param name="identifier" select="$affiliationIdentifier"/>
          <xsl:with-param name="type" select="$affiliationIdentifierScheme"/>
          <xsl:with-param name="schemeURI" select="$affiliationSchemeURI"/>
        </xsl:call-template>
      </xsl:variable>
      <xsl:if test="starts-with(translate(normalize-space($uri),$uppercase,$lowercase),'http://') or starts-with(translate(normalize-space($uri),$uppercase,$lowercase),'https://') or starts-with(translate(normalize-space($uri),$uppercase,$lowercase),'urn://')">
        <xsl:value-of select="$uri"/>
      </xsl:if>
    </xsl:param>
    <xsl:param name="affiliationIdentifierDatatype">
      <xsl:choose>
        <xsl:when test="starts-with(translate(normalize-space($affiliationIdentifier),$uppercase,$lowercase),'http://')">
          <xsl:value-of select="concat($xsd,'anyURI')"/>
        </xsl:when>
        <xsl:when test="starts-with(translate(normalize-space($affiliationIdentifier),$uppercase,$lowercase),'https://')">
          <xsl:value-of select="concat($xsd,'anyURI')"/>
        </xsl:when>
        <xsl:when test="starts-with(translate(normalize-space($affiliationIdentifier),$uppercase,$lowercase),'urn://')">
          <xsl:value-of select="concat($xsd,'anyURI')"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="concat($xsd,'string')"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:param>
    <xsl:param name="affiliationInfo">
      <xsl:if test="$affiliationIdentifier != ''">
        <dct:identifier rdf:datatype="{$affiliationIdentifierDatatype}"><xsl:value-of select="$affiliationIdentifier"/></dct:identifier>
      </xsl:if>
      <xsl:choose>
        <xsl:when test="normalize-space(@xml:lang) != ''">
          <foaf:name xml:lang="{normalize-space(@xml:lang)}"><xsl:value-of select="normalize-space(.)"/></foaf:name>
        </xsl:when>
        <xsl:otherwise>
          <foaf:name><xsl:value-of select="normalize-space(.)"/></foaf:name>
        </xsl:otherwise>
      </xsl:choose>
<!--
      <adms:identifier>
        <adms:Identifier>
          <skos:notation><xsl:value-of select="$affiliationIdentifier"/></skos:notation>
          <xsl:choose>
            <xsl:when test="$affiliationIdentifierScheme != ''">
              <adms:schemeAgency><xsl:value-of select="$affiliationIdentifierScheme"/></adms:schemeAgency>
            </xsl:when>
            <xsl:when test="$affiliationSchemeURI != ''">
              <dct:creator rdf:resource="{$affiliationSchemeURI}"/>
            </xsl:when>
          </xsl:choose>
        </adms:Identifier>
      </adms:identifier>
-->
    </xsl:param>
    <xsl:choose>
      <xsl:when test="$affiliationURI != ''">
        <foaf:Organization rdf:about="{$affiliationURI}">
          <xsl:copy-of select="$affiliationInfo"/>
        </foaf:Organization>
      </xsl:when>
      <xsl:when test="normalize-space($affiliationInfo) != ''">
        <foaf:Organization>
          <xsl:copy-of select="$affiliationInfo"/>
        </foaf:Organization>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

<!-- Funders template -->

  <xsl:template name="Funders">  
    <xsl:param name="funderIdentifier" select="normalize-space(*[local-name() = 'funderIdentifier'])"/>
<!--
    <xsl:param name="funderIdentifierType" select="translate(normalize-space(*[local-name() = 'funderIdentifier']/@funderIdentifierType),$uppercase,$lowercase)"/>
-->
    <xsl:param name="funderIdentifierType" select="normalize-space(*[local-name() = 'funderIdentifier']/@funderIdentifierType)"/>
    <xsl:param name="funderSchemeURI" select="translate(normalize-space(*[local-name() = 'funderIdentifier']/@schemeURI),$uppercase,$lowercase)"/>
    <xsl:param name="funderURI">
      <xsl:variable name="uri">
        <xsl:call-template name="IdentifierURI">
          <xsl:with-param name="identifier" select="$funderIdentifier"/>
          <xsl:with-param name="type" select="$funderIdentifierType"/>
          <xsl:with-param name="schemeURI" select="$funderSchemeURI"/>
        </xsl:call-template>
      </xsl:variable>
      <xsl:if test="starts-with(translate(normalize-space($uri),$uppercase,$lowercase),'http://') or starts-with(translate(normalize-space($uri),$uppercase,$lowercase),'https://') or starts-with(translate(normalize-space($uri),$uppercase,$lowercase),'urn://')">
        <xsl:value-of select="$uri"/>
      </xsl:if>
    </xsl:param>
    <xsl:param name="funderIdentifierDatatype">
      <xsl:choose>
        <xsl:when test="starts-with(translate(normalize-space($funderIdentifier),$uppercase,$lowercase),'http://')">
          <xsl:value-of select="concat($xsd,'anyURI')"/>
        </xsl:when>
        <xsl:when test="starts-with(translate(normalize-space($funderIdentifier),$uppercase,$lowercase),'https://')">
          <xsl:value-of select="concat($xsd,'anyURI')"/>
        </xsl:when>
        <xsl:when test="starts-with(translate(normalize-space($funderIdentifier),$uppercase,$lowercase),'urn://')">
          <xsl:value-of select="concat($xsd,'anyURI')"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="concat($xsd,'string')"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:param>
    <xsl:param name="funderInfo">
      <dct:identifier rdf:datatype="{$funderIdentifierDatatype}"><xsl:value-of select="$funderIdentifier"/></dct:identifier>
      <xsl:choose>
        <xsl:when test="normalize-space(*[local-name() = 'funderName']/@xml:lang) != ''">
          <foaf:name xml:lang="{normalize-space(*[local-name() = 'funderName']/@xml:lang)}"><xsl:value-of select="normalize-space(*[local-name() = 'funderName'])"/></foaf:name>
        </xsl:when>
        <xsl:otherwise>
          <foaf:name><xsl:value-of select="normalize-space(*[local-name() = 'funderName'])"/></foaf:name>
        </xsl:otherwise>
      </xsl:choose>
<!--
      <adms:identifier>
        <adms:Identifier>
          <skos:notation><xsl:value-of select="$funderIdentifier"/></skos:notation>
          <xsl:choose>
            <xsl:when test="$funderIdentifierType != ''">
              <adms:schemeAgency><xsl:value-of select="$funderIdentifierType"/></adms:schemeAgency>
            </xsl:when>
            <xsl:when test="$funderSchemeURI != ''">
              <dct:creator rdf:resource="{$funderSchemeURI}"/>
            </xsl:when>
          </xsl:choose>
        </adms:Identifier>
      </adms:identifier>
-->
    </xsl:param>
    <xsl:choose>
      <xsl:when test="$funderURI != ''">
        <foaf:Organization rdf:about="{$funderURI}">
          <xsl:copy-of select="$funderInfo"/>
        </foaf:Organization>
      </xsl:when>
      <xsl:when test="normalize-space($funderInfo) != ''">
        <foaf:Organization>
          <xsl:copy-of select="$funderInfo"/>
        </foaf:Organization>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

<!-- Funding Awards references template -->
<!--
  <xsl:template match="//*[local-name() = 'fundingReferences']/*[local-name() = 'fundingReference' and normalize-space(*[local-name() = 'awardNumber']/@awardURI) != '']">
-->

  <xsl:template name="FundingAwards">  
    <xsl:param name="funderIdentifier" select="normalize-space(*[local-name() = 'funderIdentifier'])"/>
    <xsl:param name="funderIdentifierType" select="translate(normalize-space(*[local-name() = 'funderIdentifier']/@funderIdentifierType),$uppercase,$lowercase)"/>
    <xsl:param name="funderURI">
      <xsl:variable name="uri">
        <xsl:call-template name="IdentifierURI">
          <xsl:with-param name="identifier" select="$funderIdentifier"/>
          <xsl:with-param name="type" select="$funderIdentifierType"/>
<!--          
          <xsl:with-param name="schemeURI" select="$schemeURI"/>
-->
        </xsl:call-template>
      </xsl:variable>
      <xsl:if test="starts-with(translate(normalize-space($uri),$uppercase,$lowercase),'http://') or starts-with(translate(normalize-space($uri),$uppercase,$lowercase),'https://') or starts-with(translate(normalize-space($uri),$uppercase,$lowercase),'urn://')">
        <xsl:value-of select="$uri"/>
      </xsl:if>
<!--    
      <xsl:if test="starts-with(translate(normalize-space(*[local-name() = 'funderIdentifier']),$uppercase,$lowercase),'http://') or starts-with(translate(normalize-space(*[local-name() = 'funderIdentifier']),$uppercase,$lowercase),'https://')">
        <xsl:value-of select="normalize-space(*[local-name() = 'funderIdentifier'])"/>
      </xsl:if>
-->
    </xsl:param>
<!--    
    <xsl:param name="funderInfo">
      <dct:identifier><xsl:value-of select="normalize-space(*[local-name() = 'funderIdentifier'])"/></dct:identifier>
      <foaf:name><xsl:value-of select="normalize-space(*[local-name() = 'funderName'])"/></foaf:name>
    </xsl:param>
-->
    <xsl:param name="fundingReferenceURI">
      <xsl:value-of select="normalize-space(*[local-name() = 'awardNumber']/@awardURI)"/>
    </xsl:param>
    <xsl:param name="fundingReferenceIdentifierDatatype">
      <xsl:choose>
        <xsl:when test="starts-with(translate(normalize-space(*[local-name() = 'awardNumber']), $uppercase, $lowercase), 'http://')">
          <xsl:value-of select="concat($xsd,'anyURI')"/>
        </xsl:when>
        <xsl:when test="starts-with(translate(normalize-space(*[local-name() = 'awardNumber']), $uppercase, $lowercase), 'https://')">
          <xsl:value-of select="concat($xsd,'anyURI')"/>
        </xsl:when>
        <xsl:when test="starts-with(translate(normalize-space(*[local-name() = 'awardNumber']), $uppercase, $lowercase), 'urn:')">
          <xsl:value-of select="concat($xsd,'anyURI')"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="concat($xsd,'string')"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:param>
    <xsl:param name="fundingReferenceInfo">
      <dct:identifier rdf:datatype="{$fundingReferenceIdentifierDatatype}"><xsl:value-of select="normalize-space(*[local-name() = 'awardNumber'])"/></dct:identifier>
      <xsl:choose>
        <xsl:when test="normalize-space(*[local-name() = 'awardTitle']/@xml:lang) != ''">
          <dct:title xml:lang="{normalize-space(*[local-name() = 'awardTitle']/@xml:lang)}"><xsl:value-of select="normalize-space(*[local-name() = 'awardTitle'])"/></dct:title>
        </xsl:when>
        <xsl:otherwise>
          <dct:title><xsl:value-of select="normalize-space(*[local-name() = 'awardTitle'])"/></dct:title>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:choose>
        <xsl:when test="$funderURI != ''">
          <frapo:isAwardedBy rdf:resource="{$funderURI}"/>
        </xsl:when>
        <xsl:when test="normalize-space(*[local-name() = 'funderName']) != '' or normalize-space(*[local-name() = 'funderIdentifier']) != ''">
          <frapo:isAwardedBy>
            <xsl:call-template name="Funders"/>
          </frapo:isAwardedBy>
        </xsl:when>
      </xsl:choose>
    </xsl:param>
    <xsl:choose>
      <xsl:when test="$fundingReferenceURI != ''">
        <foaf:Project rdf:about="{$fundingReferenceURI}">
          <xsl:copy-of select="$fundingReferenceInfo"/>
        </foaf:Project> 
      </xsl:when>
      <xsl:when test="normalize-space($fundingReferenceInfo) != ''">
        <foaf:Project>
          <xsl:copy-of select="$fundingReferenceInfo"/>
        </foaf:Project> 
      </xsl:when>
    </xsl:choose>

  </xsl:template>
  
<!-- Template returning the Alpha-2 version of a language code / tag  -->
<!-- CAVEAT: The mapping concerns just the 24 official EU languages -->
    
  <xsl:template name="LanguageAlpha2">
    <xsl:param name="langCode"/>
    <xsl:choose>
      <xsl:when test="string-length($langCode) = 2">
        <xsl:value-of select="translate($langCode,$uppercase,$lowercase)"/>
      </xsl:when>
      <xsl:when test="string-length($langCode) > 3 and string-length(substring-before($langCode, '-')) = 2">
        <xsl:value-of select="translate(substring-before($langCode, '-'),$uppercase,$lowercase)"/>
      </xsl:when>
      <xsl:when test="string-length($langCode) = 3">
        <xsl:variable name="alpha3" select="translate($langCode,$uppercase,$lowercase)"/>
        <xsl:choose>
          <xsl:when test="$alpha3 = 'bul'">
            <xsl:text>bg</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha3 = 'cze'">
            <xsl:text>cs</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha3 = 'dan'">
            <xsl:text>da</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha3 = 'ger'">  
            <xsl:text>de</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha3 = 'gre'">
            <xsl:text>el</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha3 = 'eng'">
            <xsl:text>en</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha3 = 'spa'">
            <xsl:text>es</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha3 = 'est'">
            <xsl:text>et</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha3 = 'fin'">
            <xsl:text>fi</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha3 = 'fre'">
            <xsl:text>fr</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha3 = 'gle'">
            <xsl:text>ga</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha3 = 'hrv'">
            <xsl:text>hr</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha3 = 'ita'">
            <xsl:text>it</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha3 = 'lav'">
            <xsl:text>lv</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha3 = 'lit'">
            <xsl:text>lt</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha3 = 'hun'">
            <xsl:text>hu</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha3 = 'mlt'">
            <xsl:text>mt</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha3 = 'dut'">
            <xsl:text>nl</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha3 = 'pol'">
            <xsl:text>pl</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha3 = 'por'">
            <xsl:text>pt</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha3 = 'rum'">
            <xsl:text>ru</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha3 = 'slo'">
            <xsl:text>sk</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha3 = 'slv'">
            <xsl:text>sl</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha3 = 'swe'">
            <xsl:text>sv</xsl:text>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="translate($langCode,$uppercase,$lowercase)"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

<!-- Template returning the Alpha-3 version of a language code / tag  -->
<!-- CAVEAT: The mapping concerns just the 24 official EU languages -->
    
  <xsl:template name="LanguageAlpha3">
    <xsl:param name="langCode"/>
    <xsl:variable name="alpha2">
      <xsl:choose>
        <xsl:when test="string-length($langCode) = 2">
          <xsl:value-of select="translate($langCode,$uppercase,$lowercase)"/>
        </xsl:when>
        <xsl:when test="string-length($langCode) > 3 and string-length(substring-before($langCode, '-')) = 2">
          <xsl:value-of select="translate(substring-before($langCode, '-'),$uppercase,$lowercase)"/>
        </xsl:when>
      </xsl:choose>
    </xsl:variable>
    <xsl:choose>
      <xsl:when test="string-length($langCode) = 3">
        <xsl:value-of select="translate($langCode,$uppercase,$lowercase)"/>
      </xsl:when>
      <xsl:when test="$alpha2 != ''">
        <xsl:choose>
          <xsl:when test="$alpha2 = 'bg'">
            <xsl:text>bul</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha2 = 'cs'">
            <xsl:text>cze</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha2 = 'da'">
            <xsl:text>dan</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha2 = 'de'">  
            <xsl:text>ger</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha2 = 'el'">
            <xsl:text>gre</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha2 = 'en'">
            <xsl:text>eng</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha2 = 'es'">
            <xsl:text>spa</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha2 = 'et'">
            <xsl:text>est</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha2 = 'fi'">
            <xsl:text>fin</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha2 = 'fr'">
            <xsl:text>fre</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha2 = 'ga'">
            <xsl:text>gle</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha2 = 'hr'">
            <xsl:text>hrv</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha2 = 'it'">
            <xsl:text>ita</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha2 = 'lv'">
            <xsl:text>lav</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha2 = 'lt'">
            <xsl:text>lit</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha2 = 'hu'">
            <xsl:text>hun</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha2 = 'mt'">
            <xsl:text>mlt</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha2 = 'nl'">
            <xsl:text>dut</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha2 = 'pl'">
            <xsl:text>pol</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha2 = 'pt'">
            <xsl:text>por</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha2 = 'ru'">
            <xsl:text>rum</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha2 = 'sk'">
            <xsl:text>slo</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha2 = 'sl'">
            <xsl:text>slv</xsl:text>
          </xsl:when>
          <xsl:when test="$alpha2 = 'sv'">
            <xsl:text>swe</xsl:text>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="translate($langCode,$uppercase,$lowercase)"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
    </xsl:choose>
  </xsl:template>
  
</xsl:transform>
