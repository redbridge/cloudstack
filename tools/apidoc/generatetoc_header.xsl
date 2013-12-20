<?xml version="1.0"?>
<!--
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
<xsl:output method="html" doctype-public="-//W3C//DTD HTML 1.0 Transitional//EN"/>
<xsl:template match="/">
<html class="aui" xmlns="http://www.w3.org/1999/xhtml"><head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<link rel= "stylesheet" href="includes/main.css" type="text/css" />
<link rel= "stylesheet" href="includes/aui.css" type="text/css" />
<link rel="shortcut icon" href="favicon.ico" type="image/x-icon" />

<title>RedBridge Compute API Reference</title>
</head>

<body>
<div id="insidetopbg">
<div id="inside_wrapper">
	<div class="uppermenu_panel">
            <div class="uppermenu_box"></div>
        </div>
        
        <div id="main_master">
            <div id="inside_header">
                <div>
                    <img alt="" src="./images/Large_Cloud.png" style="width: 227px; height: 137px; float:left;" />
                    <div style="font-size: 50px; font-weight: 700; font-family: 'Open Sans'; color: #0af; margin-top: 30px; margin-bottom: 30px;">
                        RedBridge
                    </div>
                    <div style="font-size: 50px; font-weight: 300; font-family: 'Open Sans' ;; color: #0af; margin-bottom: 30px;">
                       Compute 
                    </div>
                </div>
                <div style="font-size: 20px; font-weight: 700; font-family: 'Open Sans'; color: #0af; margin-top: 100px; margin-bottom: 0px;">
                    Powered by:
                </div>

                <div class="header_top">
                    <a class="cloud_logo" href="http://cloudstack.org"></a>
                    <div class="mainemenu_panel">
                        
                    </div>
                </div>
                
            
            </div>
            <div id="main_content">
             	
                <div class="inside_apileftpanel">
                	<div class="inside_contentpanel" style="width:930px;">
              		  	<!-- Modify this line for the release version -->
                         
                         <div class="api_leftsections">
                      			<h3>%API_HEADER%</h3>
                                <span>Commands available through the developer API URL and the integration API URL.</span>
                                <div class="api_legends">
           				<p><span class="api_legends_async">(A)</span> implies that the command is asynchronous.</p>
					<p>(*) implies element has a child.</p>
 				</div>
