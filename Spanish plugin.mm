<map version="freeplane 1.5.9">
<!--To view this file, download free mind mapping software Freeplane from http://freeplane.sourceforge.net -->
<node TEXT="Spanish plugin" FOLDED="false" ID="ID_1564221870" CREATED="1472866456732" MODIFIED="1472867202756" STYLE="oval">
<font SIZE="18"/>
<hook NAME="MapStyle">
    <properties fit_to_viewport="false;"/>

<map_styles>
<stylenode LOCALIZED_TEXT="styles.root_node" STYLE="oval" UNIFORM_SHAPE="true" VGAP_QUANTITY="24.0 pt">
<font SIZE="24"/>
<stylenode LOCALIZED_TEXT="styles.predefined" POSITION="right" STYLE="bubble">
<stylenode LOCALIZED_TEXT="default" COLOR="#000000" STYLE="fork">
<font NAME="SansSerif" SIZE="10" BOLD="false" ITALIC="false"/>
</stylenode>
<stylenode LOCALIZED_TEXT="defaultstyle.details"/>
<stylenode LOCALIZED_TEXT="defaultstyle.attributes">
<font SIZE="9"/>
</stylenode>
<stylenode LOCALIZED_TEXT="defaultstyle.note" COLOR="#000000" BACKGROUND_COLOR="#ffffff" TEXT_ALIGN="LEFT"/>
<stylenode LOCALIZED_TEXT="defaultstyle.floating">
<edge STYLE="hide_edge"/>
<cloud COLOR="#f0f0f0" SHAPE="ROUND_RECT"/>
</stylenode>
</stylenode>
<stylenode LOCALIZED_TEXT="styles.user-defined" POSITION="right" STYLE="bubble">
<stylenode LOCALIZED_TEXT="styles.topic" COLOR="#18898b" STYLE="fork">
<font NAME="Liberation Sans" SIZE="10" BOLD="true"/>
</stylenode>
<stylenode LOCALIZED_TEXT="styles.subtopic" COLOR="#cc3300" STYLE="fork">
<font NAME="Liberation Sans" SIZE="10" BOLD="true"/>
</stylenode>
<stylenode LOCALIZED_TEXT="styles.subsubtopic" COLOR="#669900">
<font NAME="Liberation Sans" SIZE="10" BOLD="true"/>
</stylenode>
<stylenode LOCALIZED_TEXT="styles.important">
<icon BUILTIN="yes"/>
</stylenode>
</stylenode>
<stylenode LOCALIZED_TEXT="styles.AutomaticLayout" POSITION="right" STYLE="bubble">
<stylenode LOCALIZED_TEXT="AutomaticLayout.level.root" COLOR="#000000" STYLE="oval" SHAPE_HORIZONTAL_MARGIN="10.0 pt" SHAPE_VERTICAL_MARGIN="10.0 pt">
<font SIZE="18"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,1" COLOR="#0033ff">
<font SIZE="16"/>
<edge COLOR="#ff0000"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,2" COLOR="#00b439">
<font SIZE="14"/>
<edge COLOR="#0000ff"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,3" COLOR="#990000">
<font SIZE="12"/>
<edge COLOR="#00ff00"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,4" COLOR="#111111">
<font SIZE="10"/>
<edge COLOR="#ff00ff"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,5">
<edge COLOR="#00ffff"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,6">
<edge COLOR="#7c0000"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,7">
<edge COLOR="#00007c"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,8">
<edge COLOR="#007c00"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,9">
<edge COLOR="#7c007c"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,10">
<edge COLOR="#007c7c"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,11">
<edge COLOR="#7c7c00"/>
</stylenode>
</stylenode>
</stylenode>
</map_styles>
</hook>
<hook NAME="AutomaticEdgeColor" COUNTER="14" RULE="ON_BRANCH_CREATION"/>
<node TEXT="Store verbs in db" POSITION="right" ID="ID_189230294" CREATED="1472867203948" MODIFIED="1472867229934">
<edge COLOR="#ff0000"/>
</node>
<node TEXT="Db tables" POSITION="right" ID="ID_537459784" CREATED="1472886996812" MODIFIED="1472887024549">
<edge COLOR="#0000ff"/>
<node TEXT="infinitive" ID="ID_504454852" CREATED="1472887025779" MODIFIED="1472887800320">
<node TEXT="done:connect derived infinitives" ID="ID_138390988" CREATED="1472887835014" MODIFIED="1474661017324"/>
<node TEXT="connect synonyms" ID="ID_1186679615" CREATED="1472890073487" MODIFIED="1472890079463"/>
<node TEXT="connect antonyms" ID="ID_1774813283" CREATED="1472890080422" MODIFIED="1472890086071"/>
</node>
<node TEXT="phrase" ID="ID_824484748" CREATED="1472887800894" MODIFIED="1472887803224">
<node TEXT="done:connect to primary" ID="ID_1961679699" CREATED="1472887813166" MODIFIED="1474661026159"/>
<node TEXT="connect to related" ID="ID_1768763090" CREATED="1472887825646" MODIFIED="1472887829903"/>
</node>
</node>
<node TEXT="done:Load verbs from db" POSITION="right" ID="ID_1246780781" CREATED="1472867231495" MODIFIED="1474661035533">
<edge COLOR="#0000ff"/>
</node>
<node TEXT="done:Determine what is note v. card (and document)" POSITION="right" ID="ID_216488639" CREATED="1472874029397" MODIFIED="1474661043381">
<edge COLOR="#00ffff"/>
</node>
<node TEXT="UI to list infinitives" POSITION="right" ID="ID_1567157876" CREATED="1472878892914" MODIFIED="1472878924259">
<edge COLOR="#00007c"/>
<node TEXT="determine how to create ui" ID="ID_1795709006" CREATED="1472875181385" MODIFIED="1472886974721"/>
</node>
<node TEXT="Generate infinitive cards from loaded infinitives" POSITION="right" ID="ID_1582017235" CREATED="1472878937369" MODIFIED="1472882673538">
<arrowlink SHAPE="CUBIC_CURVE" COLOR="#000000" WIDTH="2" TRANSPARENCY="200" FONT_SIZE="9" FONT_FAMILY="SansSerif" DESTINATION="ID_1954249768" STARTINCLINATION="57;0;" ENDINCLINATION="57;0;" STARTARROW="NONE" ENDARROW="DEFAULT"/>
<edge COLOR="#7c007c"/>
<node TEXT="" ID="ID_1603372492" CREATED="1474661067097" MODIFIED="1474661067097"/>
</node>
<node TEXT="Generic Code to generate Notes and Cards" POSITION="right" ID="ID_1954249768" CREATED="1472878997246" MODIFIED="1472879020216">
<edge COLOR="#ff0000"/>
<node TEXT="Generate Notes" ID="ID_1350304891" CREATED="1472874001814" MODIFIED="1472879037702"/>
<node TEXT="Generate Cards" ID="ID_441378939" CREATED="1472874025269" MODIFIED="1472879030367"/>
</node>
</node>
</map>
