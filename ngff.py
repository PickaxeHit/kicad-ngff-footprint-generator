from __future__ import division
import pcbnew
import FootprintWizardBase

keying = {
    "A": {
        "KeyCenter": 6.625,
        "PinMin": 8,
        "PinMax": 15,
    },
    "B": {
        "KeyCenter": 5.625,
        "PinMin": 12,
        "PinMax": 19,
    },
    "C": {
        "KeyCenter": 4.625,
        "PinMin": 16,
        "PinMax": 23,
    },
    "D": {
        "KeyCenter": 3.625,
        "PinMin": 20,
        "PinMax": 27,
    },
    "E": {
        "KeyCenter": 2.625,
        "PinMin": 24,
        "PinMax": 31,
    },
    "F": {
        "KeyCenter": 1.625,
        "PinMin": 28,
        "PinMax": 35,
    },
    "G": {
        "KeyCenter": -1.125,
        "PinMin": 39,
        "PinMax": 46,
    },
    "H": {
        "KeyCenter": -2.125,
        "PinMin": 43,
        "PinMax": 50,
    },
    "J": {
        "KeyCenter": -3.125,
        "PinMin": 47,
        "PinMax": 54,
    },
    "K": {
        "KeyCenter": -4.125,
        "PinMin": 51,
        "PinMax": 58,
    },
    "L": {
        "KeyCenter": -5.125,
        "PinMin": 55,
        "PinMax": 62,
    },
    "M": {
        "KeyCenter": -6.125,
        "PinMin": 59,
        "PinMax": 66,
    },
}

connectorHeight = pcbnew.FromMM(4.0)

connectorTotalWidth = pcbnew.FromMM(22.0)
connectorTongueWidth = pcbnew.FromMM(19.85)

connectorBaseArcRadius = pcbnew.FromMM(0.50)
connectorBaseLength = (connectorTotalWidth - connectorTongueWidth) / 2.0 - connectorBaseArcRadius;

padWidth = pcbnew.FromMM(0.35)
padPitch = pcbnew.FromMM(0.50)
mPadTopWidth = pcbnew.FromMM(5.50)
mPadTopHeight = pcbnew.FromMM(5.50)
mPadBottomWidth = pcbnew.FromMM(6.0)
mPadBottomHeight = pcbnew.FromMM(6.0 + 1.0)

topPadHeight = pcbnew.FromMM(2.0)
bottomPadHeight = pcbnew.FromMM(2.50)
padVerticalOffset = pcbnew.FromMM(0.55)

topKeepout = pcbnew.FromMM(4.0)
bottomKeepout = pcbnew.FromMM(5.20)

keyDiameter = pcbnew.FromMM(1.20)
keyHeight = pcbnew.FromMM(3.50)

connectorTopKeepout = pcbnew.FromMM(4.0)
connectorBottomKeepout = pcbnew.FromMM(5.20)

class NGFF_FootprintWizard(FootprintWizardBase.FootprintWizard):
    def GetName(self):
        return "NGFF (M.2) Edge Connector"

    def GetDescription(self):
        return "NGFF (M.2) Edge Connector Wizard"

    def GetValue(self):
        first = self.GetParam("Keying", "First").value
        second = self.GetParam("Keying", "Second").value

        width = self.GetParam("Size", "Width").value
        length = self.GetParam("Size", "Length").value

        widthMM = int(pcbnew.ToMM(width))
        lengthMM = int(pcbnew.ToMM(length))

        if width and length:
            if first:
                if second:
                    return "NGFF_%s+%s_%s%s" % (first, second, widthMM, lengthMM)
                else:
                    return "NGFF_%s_%s%s" % (first, widthMM, lengthMM)
            elif second:
                return "NGFF_%s_%s%s" % (second, widthMM, lengthMM)
            else:
                return "NGFF_%s%s" % (widthMM, lengthMM)
        else:
            if first:
                if second:
                    return "NGFF_%s+%s" % (first, second)
                else:
                    return "NGFF_%s" % first
            elif second:
                return "NGFF_%s" % second
            else:
                return "NGFF"

    def GenerateParameterList(self):
        self.AddParam("Keying", "First", self.uString, "B")
        self.AddParam("Keying", "Second", self.uString, "M")
        self.AddParam("Size", "Width", self.uMM, 22)
        self.AddParam("Size", "Length", self.uMM, 80)

    def firstKey(self):
        first = self.GetParam("Keying", "First").value
        return keying.get(first, None)

    def secondKey(self):
        second = self.GetParam("Keying", "Second").value
        return keying.get(second, None)

    def omitPin(self, number):
        firstKey = self.firstKey()
        if firstKey and firstKey["PinMin"] <= number <= firstKey["PinMax"]:
            return True

        secondKey = self.secondKey()
        if secondKey and secondKey["PinMin"] <= number <= secondKey["PinMax"]:
            return True

    def createPad(self, number, name):
        top = number % 2 == 1

        if self.omitPin(number):
            return None

        padTotalHeight = topPadHeight if top else bottomPadHeight
        padHeight = padTotalHeight - padVerticalOffset

        padSize = pcbnew.VECTOR2I(int(padWidth), int(padHeight))

        padOneCenterX = int(pcbnew.FromMM(18 * 0.5 + 0.25))
        padTwoCenterX = padOneCenterX + int(pcbnew.FromMM(0.25))

        pad = pcbnew.PAD(self.module)
        layerSet = pcbnew.LSET()

        if top:
            padOffset = (number - 1) / 2
            padCenterX = padOneCenterX - int(padOffset * pcbnew.FromMM(0.5))
            layerSet.AddLayer(pcbnew.F_Cu)
        else:
            padOffset = number / 2
            padCenterX = padTwoCenterX - int(padOffset * pcbnew.FromMM(0.5))
            layerSet.AddLayer(pcbnew.B_Cu)

        padCenterY = -int(padVerticalOffset + padHeight / 2.0)
        padCenter = pcbnew.VECTOR2I(padCenterX, padCenterY)

        pad.SetSize(padSize)
        pad.SetPos(padCenter)
        pad.SetPosition(padCenter)
        pad.SetShape(pcbnew.PAD_SHAPE_RECT)
        pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        pad.SetLayerSet(layerSet)
        pad.SetName(name)
        return pad

    def createMechanicalPad(self, height, layer):
        pad = pcbnew.PAD(self.module)
        layerSet = pcbnew.LSET()
        layerSet.AddLayer(layer)
        pad.SetName('MP')

        if layer == pcbnew.F_Cu:
            mPadCenterX = 0.0
            mPadCenterY = height
            pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
            pad.SetShape(pcbnew.PAD_SHAPE_OVAL)
            pad.SetSizeX(mPadTopWidth)
            pad.SetSizeY(mPadTopHeight)
            pad.SetX(int(mPadCenterX))
            pad.SetY(-int(mPadCenterY))
            layerSet.AddLayer(pcbnew.F_Mask)
        elif layer == pcbnew.B_Cu:
            mPadCenterX = 0.0
            mPadCenterY = height - pcbnew.FromMM(0.50)
            pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
            pad.SetShape(pcbnew.PAD_SHAPE_OVAL)
            pad.SetSizeX(mPadBottomWidth)
            pad.SetSizeY(mPadBottomHeight)
            pad.SetX(int(mPadCenterX))
            pad.SetY(-int(mPadCenterY))
            layerSet.AddLayer(pcbnew.B_Mask)

        pad.SetLayerSet(layerSet)

        return pad

    def Arc(self, cx, cy, sx, sy, a):
        circle = pcbnew.PCB_SHAPE(self.module)
        circle.SetWidth(self.draw.dc['lineThickness'])
        circle.SetLayer(pcbnew.Edge_Cuts)
        circle.SetShape(pcbnew.SHAPE_T_ARC)

        center = self.draw.TransformPoint(cx, cy)
        start = self.draw.TransformPoint(sx, sy)

        circle.SetCenter(center)
        circle.SetStart(start)

        angle = pcbnew.EDA_ANGLE(a, pcbnew.TENTHS_OF_A_DEGREE_T)

        circle.SetArcAngleAndEnd(angle, True)

        self.module.Add(circle)

    def CheckParameters(self):
        first = self.GetParam("Keying", "First")
        second = self.GetParam("Keying", "Second")
        width = self.GetParam("Size", "Width")
        length = self.GetParam("Size", "Length")
        if first.value and first.value not in keying:
            msg = "Unknown first keying: %s (supported: %s)" % (first, ", ".join(sorted(keying.keys())))
            first.AddError(msg)

        if second.value and second.value not in keying:
            msg = "Unknown second keying: %s (supported: %s)" % (second, ", ".join(sorted(keying.keys())))
            second.AddError(msg)

        if first.value and second.value:
            if ord(first.value) > ord(second.value):
                f, s = first.value, second.value
                second.SetValue(f)
                first.SetValue(s)

            is_ascii_diff_1 = (ord(second.value) - ord(first.value) == 1)
            is_fg_pair = (first.value == 'F' and second.value == 'G')
            is_hj_pair = (first.value == 'H' and second.value == 'J')

            if (is_ascii_diff_1 and not is_fg_pair) or is_hj_pair:
                msg = f"Keying overlap for keying {first.value} and {second.value} is not supported yet"
                first.AddError(msg)
                second.AddError(msg)

        if width.value and length.value:
            if width.value < pcbnew.FromMM(22):
                msg = f"{width} is too small and not supported yet, expected >= 22"
                width.AddError(msg)

            if length.value < pcbnew.FromMM(12):
                msg = f"{length} is too small and not supported yet, expected >= 12"
                length.AddError(msg)


    def FilledBox(self, x1, y1, x2, y2):
        box = pcbnew.PCB_SHAPE(self.module)
        box.SetShape(pcbnew.SHAPE_T_POLY)
        box.SetFilled(True)

        corners = [
            pcbnew.VECTOR2I(int(x1), int(y1)),
            pcbnew.VECTOR2I(int(x2), int(y1)),
            pcbnew.VECTOR2I(int(x2), int(y2)),
            pcbnew.VECTOR2I(int(x1), int(y2)),
            pcbnew.VECTOR2I(int(x1), int(y1))
        ]

        box.SetPolyPoints(corners)
        return box

    def Zone(self, x1, y1, x2, y2):
        zone = pcbnew.ZONE(self.module)
        zone.SetDoNotAllowCopperPour(False)
        zone.SetDoNotAllowVias(False)
        zone.SetDoNotAllowTracks(False)
        zone.SetDoNotAllowPads(False)
        zone.SetDoNotAllowFootprints(False)


        corners = [
            pcbnew.VECTOR2I(int(x1), int(y1)),
            pcbnew.VECTOR2I(int(x2), int(y1)),
            pcbnew.VECTOR2I(int(x2), int(y2)),
            pcbnew.VECTOR2I(int(x1), int(y2)),
            pcbnew.VECTOR2I(int(x1), int(y1))
        ]

        outline = zone.Outline()
        outline.RemoveAllContours()
        outline.NewOutline()

        for x, y in corners:
            outline.Append(x, y)

        return zone

    def drawRuleAreaNoPour(self, x1, x2, height, layer):
        rectCenterX = pcbnew.FromMM(0.0)
        rectCenterY = -height / 2.0

        zone = self.Zone(x1, pcbnew.FromMM(0.0), x2, -height)
        zone.SetLayer(layer)
        zone.SetIsRuleArea(True)
        zone.SetDoNotAllowCopperPour(True)
        zone.SetZoneName('NoCopperPourZone')
        self.draw.module.Add(zone)

    def drawRuleAreaNoFootprints(self, x1, x2, height, layer):
        rectCenterX = pcbnew.FromMM(0.0)
        rectCenterY = -height / 2.0

        zone = self.Zone(x1, pcbnew.FromMM(0.0), x2, -height)
        zone.SetLayer(layer)
        zone.SetIsRuleArea(True)
        zone.SetDoNotAllowFootprints(True)
        zone.SetZoneName('NoFootprintsZone')
        self.draw.module.Add(zone)

    def drawSolderMaskOpening(self, x1, x2, height, layer):
        rectCenterX = pcbnew.FromMM(0.0)
        rectCenterY = -height / 2.0

        box = self.FilledBox(x1, pcbnew.FromMM(0.0), x2, -height)
        box.SetLayer(layer)
        self.draw.module.Add(box)

    def BuildThisFootprint(self):
        draw = self.draw
        draw.SetLineThickness(pcbnew.FromMM(0.05))
        draw.Value(0, pcbnew.FromMM(2.0), self.GetTextSize())
        draw.Reference(0, pcbnew.FromMM(4.0), self.GetTextSize())

        draw.SetLayer(pcbnew.Edge_Cuts)
        centerX = centerY = pcbnew.FromMM(0.0)

        bottomEndpoints = []

        topLeftX = -connectorTotalWidth / 2.0
        topLeftY = -connectorHeight

        topLeftArcStartX = topLeftX + connectorBaseLength
        topLeftArcStartY = topLeftY

        draw.Line(topLeftX, topLeftY, topLeftArcStartX, topLeftY)

        topLeftArcCenterX = topLeftArcStartX
        topLeftArcCenterY = topLeftArcStartY + connectorBaseArcRadius
        topLeftArcAngle = 900

        self.Arc(topLeftArcCenterX, topLeftArcCenterY, topLeftArcStartX, topLeftArcStartY, topLeftArcAngle)

        topLeftArcEndX = topLeftArcStartX + connectorBaseArcRadius
        topLeftArcEndY = topLeftArcStartY + connectorBaseArcRadius

        bottomLeftX = topLeftArcEndX
        bottomLeftY = topLeftArcEndY + connectorHeight - connectorBaseArcRadius

        bottomEndpoints.append(bottomLeftX)

        draw.Line(topLeftArcEndX, topLeftArcEndY, bottomLeftX, bottomLeftY)

        KeyArcAngle = 1800

        def draw_key(KeyCenter):
            leftX = centerX + KeyCenter - keyDiameter / 2.0
            rightX = leftX + keyDiameter
            topY = centerY - keyHeight + keyDiameter / 2.0
            draw.Line(leftX, centerY, leftX, topY)
            draw.Line(rightX, centerY, rightX, topY)
            self.Arc(KeyCenter, topY, leftX, topY, KeyArcAngle)

        for key in [self.secondKey(), self.firstKey()]:
            if key:
                KeyCenter = pcbnew.FromMM(key["KeyCenter"])
                draw_key(KeyCenter)

                leftX = centerX + KeyCenter - keyDiameter / 2.0
                rightX = leftX + keyDiameter

                bottomEndpoints += [leftX, rightX]

        bottomRightX = connectorTongueWidth / 2.0
        bottomRightY = centerY

        topRightArcStartX = bottomRightX
        topRightArcStartY = bottomRightY - connectorHeight + connectorBaseArcRadius

        bottomEndpoints.append(bottomRightX)

        draw.Line(bottomRightX, bottomRightY, topRightArcStartX, topRightArcStartY)

        topRightArcCenterX = topRightArcStartX + connectorBaseArcRadius
        topRightArcCenterY = topRightArcStartY
        topRightArcAngle = 900

        self.Arc(topRightArcCenterX, topRightArcCenterY, topRightArcStartX, topRightArcStartY, topRightArcAngle)

        topRightArcEndX = topRightArcStartX + connectorBaseArcRadius
        topRightArcEndY = topRightArcStartY - connectorBaseArcRadius

        topRightX = connectorTotalWidth /2.0
        topRightY = -connectorHeight

        draw.Line(topRightArcEndX, topRightArcEndY, topRightX, topRightY)

        for endpoints in zip(bottomEndpoints[0::2], bottomEndpoints[1::2]):
            self.drawSolderMaskOpening(endpoints[0], endpoints[1], topPadHeight, pcbnew.F_Mask)
            self.drawSolderMaskOpening(endpoints[0], endpoints[1], bottomPadHeight, pcbnew.B_Mask)
            draw.Line(endpoints[0], centerY, endpoints[1], centerY)

        self.drawRuleAreaNoPour(bottomRightX, -bottomRightX, topPadHeight, pcbnew.F_Cu)
        self.drawRuleAreaNoPour(bottomRightX, -bottomRightX, bottomPadHeight, pcbnew.B_Cu)

        self.drawRuleAreaNoFootprints(topRightX, -topRightX, connectorTopKeepout, pcbnew.F_Cu)
        self.drawRuleAreaNoFootprints(topRightX, -topRightX, connectorBottomKeepout, pcbnew.B_Cu)

        for padNumber in range(1, 76):
            pad = self.createPad(padNumber, str(padNumber))
            if pad:
                self.module.Add(pad)

        width = self.GetParam("Size", "Width")
        length = self.GetParam("Size", "Length")

        if width.value > 0 and length.value > 0:
            if width.value > connectorTotalWidth:
                bottomBorderStartX = connectorTotalWidth / 2
                bottomBorderStartY = -connectorHeight
                bottomBorderEndX = connectorTotalWidth / 2.0 + (width.value - connectorTotalWidth) / 2.0
                bottomBorderEndY = -connectorHeight
                draw.Line(-bottomBorderStartX, bottomBorderStartY, -bottomBorderEndX, bottomBorderEndY)
                draw.Line(bottomBorderStartX, bottomBorderStartY, bottomBorderEndX, bottomBorderEndY)

            leftBorderStartX = - connectorTotalWidth / 2.0 - (width.value - connectorTotalWidth) / 2.0
            leftBorderStartY = -connectorHeight
            leftBorderEndX = leftBorderStartX
            leftBorderEndY = -length.value
            topArcStartX = -pcbnew.FromMM(3.5 / 2.0)
            draw.Line(leftBorderStartX, leftBorderStartY, leftBorderEndX, leftBorderEndY)
            draw.Line(-leftBorderStartX, leftBorderStartY, -leftBorderEndX, leftBorderEndY)
            draw.Line(leftBorderEndX, leftBorderEndY, topArcStartX, leftBorderEndY)
            draw.Line(-leftBorderEndX, leftBorderEndY, -topArcStartX, leftBorderEndY)

            self.Arc(0.0, -length.value, topArcStartX, -length.value, -1800)

            pad = self.createMechanicalPad(length.value, pcbnew.F_Cu)
            self.module.Add(pad)

            pad = self.createMechanicalPad(length.value, pcbnew.B_Cu)
            self.module.Add(pad)

NGFF_FootprintWizard().register()
