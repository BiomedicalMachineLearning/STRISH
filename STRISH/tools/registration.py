from skimage import measure
from scipy import ndimage as ndi
import cv2
import SimpleITK as sitk
from ..utils import *
import matplotlib.pyplot as plt
from typing import Any, Union, Optional
from pathlib import Path

def start_plot():
    """Setup data for plotting

    Invoked when StartEvent happens at the beginning of registration.
    """
    global metric_values, multires_iterations

    metric_values = []
    multires_iterations = []

def end_plot():
    """Cleanup the data and figures
    """
    global metric_values, multires_iterations

    del metric_values
    del multires_iterations
    # Close figure, we don't want to get a duplicate of the plot latter on.
    plt.close()


def update_plot(registration_method):
    """Plot metric value after each registration iteration

    Invoked when IterationEvent happens.
    """
    global metric_values, multires_iterations

    metric_values.append(registration_method.GetMetricValue())
    # Clear the output area (wait=True, to reduce flickering), and plot current data
    # clear_output(wait=True)
    # Plot the similarity metric values
    plt.plot(metric_values, 'r')
    plt.plot(multires_iterations, [metric_values[index] for index in multires_iterations], 'b*')
    plt.xlabel('Iteration Number', fontsize=12)
    plt.ylabel('Metric', fontsize=12)
    plt.show()


def update_multires_iterations():
    """Update the index in the metric values list that corresponds to a change in registration resolution

    Invoked when the sitkMultiResolutionIterationEvent happens.
    """
    global metric_values, multires_iterations
    multires_iterations.append(len(metric_values))


def plot_metric(title='Plot of registration metric vs iterations'):
    """Plots the mutual information over registration iterations

    Parameters
    ----------
    title : str

    Returns
    -------
    fig : matplotlib figure
    """
    global metric_values, multires_iterations

    fig, ax = plt.subplots()
    ax.set_title(title)
    ax.set_xlabel('Iteration Number', fontsize=12)
    ax.set_ylabel('Mutual Information Cost', fontsize=12)
    ax.plot(metric_values, 'r')
    ax.plot(multires_iterations, [metric_values[index] for index in multires_iterations], 'b*',
            label='change in resolution')
    ax.legend()
    return fig


def affine_registration_slides(fixed_ref_img, moving_img):
    initial_transform = sitk.CenteredTransformInitializer(fixed_ref_img, moving_img, sitk.Euler2DTransform(),
                                                          sitk.CenteredTransformInitializerFilter.GEOMETRY)
    affine_method = sitk.ImageRegistrationMethod()

    # Similarity metric settings.
    affine_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=75)
    affine_method.SetMetricSamplingStrategy(affine_method.RANDOM)
    affine_method.SetMetricSamplingPercentage(0.15)

    affine_method.SetInterpolator(sitk.sitkLinear)

    # Optimizer settings.
    affine_method.SetOptimizerAsGradientDescent(learningRate=1, numberOfIterations=300, convergenceMinimumValue=1e-6,
                                                convergenceWindowSize=20)
    affine_method.SetOptimizerScalesFromPhysicalShift()

    # Setup for the multi-resolution framework.
    affine_method.SetShrinkFactorsPerLevel(shrinkFactors=[16, 8, 4, 3, 2, 1])
    affine_method.SetSmoothingSigmasPerLevel(smoothingSigmas=[10, 4, 3, 2, 1, 0])
    affine_method.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()

    # Don't optimize in-place, we would possibly like to run this cell multiple times.
    affine_method.SetInitialTransform(initial_transform, inPlace=False)

    # Connect all of the observers so that we can perform plotting during registration.
    affine_method.AddCommand(sitk.sitkStartEvent, start_plot)
    affine_method.AddCommand(sitk.sitkEndEvent, end_plot)
    affine_method.AddCommand(sitk.sitkMultiResolutionIterationEvent, update_multires_iterations)
    affine_method.AddCommand(sitk.sitkIterationEvent, lambda: update_plot(affine_method))

    affine_transform = affine_method.Execute(sitk.Cast(fixed_ref_img, sitk.sitkFloat32),
                                             sitk.Cast(moving_img, sitk.sitkFloat32))
    return affine_transform


def bspline_registration_slides(fixed_ref_img, moving_img):
    bspline_method = sitk.ImageRegistrationMethod()

    # Similarity metric settings.
    bspline_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)
    bspline_method.SetMetricSamplingStrategy(bspline_method.RANDOM)
    bspline_method.SetMetricSamplingPercentage(0.15)

    bspline_method.SetInterpolator(sitk.sitkLinear)

    # Optimizer settings.
    bspline_method.SetOptimizerAsGradientDescent(learningRate=1, numberOfIterations=75, convergenceMinimumValue=1e-6,
                                                 convergenceWindowSize=10)
    bspline_method.SetOptimizerScalesFromPhysicalShift()

    # Setup for the multi-resolution framework.
    bspline_method.SetShrinkFactorsPerLevel(shrinkFactors=[2, 1])
    bspline_method.SetSmoothingSigmasPerLevel(smoothingSigmas=[1, 0])
    bspline_method.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()

    # Don't optimize in-place, we would possibly like to run this cell multiple times.
    transformDomainMeshSize = [8] * moving_img.GetDimension()
    initial_transform = sitk.BSplineTransformInitializer(fixed_ref_img, transformDomainMeshSize)
    bspline_method.SetInitialTransform(initial_transform, inPlace=False)

    # Connect all of the observers so that we can perform plotting during registration.
    bspline_method.AddCommand(sitk.sitkStartEvent, start_plot)
    bspline_method.AddCommand(sitk.sitkEndEvent, end_plot)
    bspline_method.AddCommand(sitk.sitkMultiResolutionIterationEvent, update_multires_iterations)
    bspline_method.AddCommand(sitk.sitkIterationEvent, lambda: update_plot(bspline_method))

    bspline_transform = bspline_method.Execute(sitk.Cast(fixed_ref_img, sitk.sitkFloat32),
                                               sitk.Cast(moving_img, sitk.sitkFloat32))
    return bspline_transform


def inverse_transform_multiple_points(xform, points):
    """
    Perform points transformation using xform as a transformation model
    """
    transformed_points = list()
    for point in points:
        result, state = inverse_transform_point(xform, point)
        transformed_points.append(result)
    return transformed_points

def save_transformation_model(transform_model, fn:Union[str, Path]):
    sitk.WriteTransform(transform_model, fn)