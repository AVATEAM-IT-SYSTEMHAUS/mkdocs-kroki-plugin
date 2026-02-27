# Other Diagram Formats

Additional diagram types supported through Kroki.

## UMLet

UMLet uses an XML-based format for UML diagrams.

### Class Diagram

```umlet
<?xml version="1.0" encoding="UTF-8"?>
<diagram program="umlet" version="14.3.0">
  <zoom_level>10</zoom_level>
  <element>
    <id>UMLClass</id>
    <coordinates>
      <x>10</x>
      <y>10</y>
      <w>210</w>
      <h>110</h>
    </coordinates>
    <panel_attributes>User
--
+name: String
+email: String
+role: Role
--
+login(): boolean
+logout(): void</panel_attributes>
  </element>
  <element>
    <id>UMLClass</id>
    <coordinates>
      <x>290</x>
      <y>10</y>
      <w>210</w>
      <h>90</h>
    </coordinates>
    <panel_attributes>Session
--
+token: String
+expiresAt: Date
--
+isValid(): boolean</panel_attributes>
  </element>
  <element>
    <id>Relation</id>
    <coordinates>
      <x>210</x>
      <y>40</y>
      <w>100</w>
      <h>40</h>
    </coordinates>
    <panel_attributes>lt=-&gt;
m1=1
m2=0..*</panel_attributes>
    <additional_attributes>10;10;80;10</additional_attributes>
  </element>
</diagram>
```

## BPMN

Business Process Model and Notation uses XML to define business workflows.

### Order Processing

```bpmn
<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL"
             xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
             xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
             xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
             id="definitions"
             targetNamespace="http://example.com">
  <process id="Process_1" isExecutable="false">
    <startEvent id="start" name="Order Received"/>
    <task id="task1" name="Validate Order"/>
    <exclusiveGateway id="gw1" name="Valid?"/>
    <task id="task2" name="Process Payment"/>
    <task id="task3" name="Reject Order"/>
    <endEvent id="end1" name="Complete"/>
    <endEvent id="end2" name="Rejected"/>
    <sequenceFlow id="f1" sourceRef="start" targetRef="task1"/>
    <sequenceFlow id="f2" sourceRef="task1" targetRef="gw1"/>
    <sequenceFlow id="f3" sourceRef="gw1" targetRef="task2" name="Yes"/>
    <sequenceFlow id="f4" sourceRef="gw1" targetRef="task3" name="No"/>
    <sequenceFlow id="f5" sourceRef="task2" targetRef="end1"/>
    <sequenceFlow id="f6" sourceRef="task3" targetRef="end2"/>
  </process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1">
      <bpmndi:BPMNShape id="start_di" bpmnElement="start">
        <dc:Bounds x="180" y="160" width="36" height="36"/>
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="task1_di" bpmnElement="task1">
        <dc:Bounds x="270" y="138" width="100" height="80"/>
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="gw1_di" bpmnElement="gw1" isMarkerVisible="true">
        <dc:Bounds x="425" y="153" width="50" height="50"/>
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="task2_di" bpmnElement="task2">
        <dc:Bounds x="530" y="80" width="100" height="80"/>
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="task3_di" bpmnElement="task3">
        <dc:Bounds x="530" y="210" width="100" height="80"/>
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="end1_di" bpmnElement="end1">
        <dc:Bounds x="690" y="102" width="36" height="36"/>
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="end2_di" bpmnElement="end2">
        <dc:Bounds x="690" y="232" width="36" height="36"/>
      </bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="f1_di" bpmnElement="f1">
        <di:waypoint x="216" y="178"/>
        <di:waypoint x="270" y="178"/>
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="f2_di" bpmnElement="f2">
        <di:waypoint x="370" y="178"/>
        <di:waypoint x="425" y="178"/>
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="f3_di" bpmnElement="f3">
        <di:waypoint x="450" y="153"/>
        <di:waypoint x="450" y="120"/>
        <di:waypoint x="530" y="120"/>
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="f4_di" bpmnElement="f4">
        <di:waypoint x="450" y="203"/>
        <di:waypoint x="450" y="250"/>
        <di:waypoint x="530" y="250"/>
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="f5_di" bpmnElement="f5">
        <di:waypoint x="630" y="120"/>
        <di:waypoint x="690" y="120"/>
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="f6_di" bpmnElement="f6">
        <di:waypoint x="630" y="250"/>
        <di:waypoint x="690" y="250"/>
      </bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</definitions>
```
