import qupath.ext.stardist.StarDist2D
import qupath.lib.gui.tools.MeasurementExporter
import qupath.lib.objects.PathCellObject


def pathModel = '/Volumes/BiomedML/Projects/QuPath_projects/CellSegmentationModels/dsb2018_heavy_augment.pb'
println('Begin')
def stardist = StarDist2D.builder(pathModel)
        .threshold(0.006)             // Probability (detection) threshold
        .channels('Original')            // Select detection channel  // Percentile normalization
        .normalizePercentiles(1, 95)
        .pixelSize(0.05)              // Resolution for detection
        .cellExpansion(0.01)          // Approximate cells based upon nucleus expansion
        .cellConstrainScale(1.5)     // Constrain cell expansion using nucleus size
        .measureShape()              // Add shape measurements
        .measureIntensity()          // Add cell measurements (in all compartments)
        .includeProbability(true)    // Add probability as a measurement (enables later filtering)
        .build()

// Run detection for the selected objects
def imageData = getCurrentImageData()
def pathObjects = getSelectedObjects()
if (pathObjects.isEmpty()) {
    Dialogs.showErrorMessage("StarDist", "Please select a parent object!")
    return
}

stardist.detectObjects(imageData, pathObjects)


String filename1 =  String.format('/Volumes/BiomedML/Projects/QuPath_projects/Polaris/0429_Detection_100c/Detected_cells.tsv')
        // def outputPath = "/Volumes/BiomedML/Projects/QuPath_projects/Covid19/scripts/Demo_measurements.tsv"
// def columnsToInclude = new String[]{"Image", "Centroid X µm","Centroid Y µm", "Nucleus: Area", "Nucleus: DAPI (DAPI) mean", "Cell: DAPI (DAPI) mean", "Nucleus: PD-L1 (Opal 520) mean", "Cell: PD-L1 (Opal 520) mean","Nucleus: PD-1 (Opal 620) mean", "Cell: PD-1 (Opal 620) mean", "Nucleus: Perimeter", "Nucleus: Circularity","Nucleus: Eccentricity" }
def outputFile1 = new File(filename1)
def separator = "\t"
def imagesToExport = [getProjectEntry()]
def exportType = PathCellObject.class
// print(columnsToInclude.getClass())
def exporter  = new MeasurementExporter()
                  .imageList(imagesToExport)            // Images from which measurements will be exported
                  .separator(separator)                 // Character that separates values
                  .exportType(exportType)               // Type of objects to export
                  .exportMeasurements(filename1)        // Start the export process

// print("Done")
println('Done')