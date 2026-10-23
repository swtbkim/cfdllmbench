# Rectangular_Obstacle_SA
| | |
|---|---|
| Solver | `pimpleFoam` |
| Turbulence | RAS SpalartAllmaras |
| Mesh cells (blockMesh) | 55000 |
| endTime / deltaT / writeInterval | 5 / 0.5 / 0.5 |
| Reference files | 12 |

## Prompt (`usr_requirement`)

> Perform an incompressible turbulent flow simulation over a 2D rectangular obstacle using the SpalartAllmaras turbulence model and pimpleFoam solver. The computational domain spans 0 to 15 in x direction and 0 to 5 in y direction and -0.5 to 0.5 in z direction. The rectangular obstacle is of size  1 unit x 1 unit x 1 unit centered at 2.5 x 2.5 x 0.0. Use one cell in z direction making the geometry effectively 2D. Refine the mesh near to rectangle. Use sufficient grid points to discretize the domain and dont use more than 60000 cells in your mesh. The left boundary is the inlet which uses a uniform velocity of (1,0,0) m/s. The right boundary is the outlet, with fixed-value pressure equal to the internal field value of 101325 and a pressureInletOutletVelocity condition for velocity. Top and bottom boundaries are fixed walls with no-slip condition. The front and back faces are empty. The rectangular obstacle also has no-slip boundary condition on its surface. The kinematic viscosity is 2e-6 m2/s. Use a deltaT of 0.5 s and run till a final time of 5 s. Write the results at every 0.5 s. Use a maximum courant number of 1.0.

## Reference files

- `Allrun`
- `system/fvSolution`
- `system/controlDict`
- `system/decomposeParDict`
- `system/fvSchemes`
- `system/blockMeshDict`
- `0/nuTilda`
- `0/p`
- `0/U`
- `0/nut`
- `constant/turbulenceProperties`
- `constant/transportProperties`

### `Allrun`

```sh
#!/bin/sh
cd ${0%/*} || exit 1    # Run from this directory

# Source tutorial run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

application="pimpleFoam"

runApplication blockMesh
runApplication $application
```

### `system/fvSolution`

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  v2412                                 |
|   \  /    A nd           | Website:  www.openfoam.com                      |
|    \/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      fvSolution;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

solvers
{
    "(p|pcorr)"
    {
        solver          GAMG;
        smoother        DICGaussSeidel;
        tolerance       1e-06;
        relTol          0.1;
    }
    "(p|pcorr)Final"
    {
        $p;
        tolerance       1e-06;
        relTol          0;
    }
    "(U|k|omega)"
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-06;
        relTol          0.1;
    }
    "(nuTilda|nuTildaFinal)"
     {
         solver          smoothSolver;
         smoother        GaussSeidel;
         tolerance       1e-6;
         relTol          0.1;
     }
    "(U|k|omega)Final"
    {
        $U;
        tolerance       1e-06;
        relTol          0;
    }
}


PIMPLE
{
    momentumPredictor   yes;
    nOuterCorrectors    2;
    nCorrectors     2;
    nNonOrthogonalCorrectors 0;
}

// ************************************************************************* //
```

### `system/controlDict`

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  v2412                                 |
|   \  /    A nd           | Website:  www.openfoam.com                      |
|    \/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      controlDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

application     pimpleFoam;

startFrom       latestTime;

startTime       0;

stopAt          endTime;

endTime         5;

deltaT          0.5;

writeControl    adjustableRunTime;

writeInterval   0.5;
purgeWrite      0;

writeFormat     ascii;

writePrecision  6;

writeCompression off;

timeFormat      general;

timePrecision   6;

runTimeModifiable yes;

adjustTimeStep  yes;

maxCo           1;

// ************************************************************************* //
```

### `system/decomposeParDict`

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  v2412                                 |
|   \  /    A nd           | Website:  www.openfoam.com                      |
|    \/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      decomposeParDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

numberOfSubdomains 6;

method          hierarchical;

coeffs
{
    n           (3 2 1);
}


// ************************************************************************* //
```

### `system/fvSchemes`

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  v2412                                 |
|   \  /    A nd           | Website:  www.openfoam.com                      |
|    \/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      fvSchemes;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

ddtSchemes
{
    default         Euler;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default         none;
    div(U)          Gauss linear;
    div(phi,U)      Gauss linearUpwind grad(U);
    div(phi,k)      Gauss linearUpwind grad(U);
    div(phi,K)      Gauss linearUpwind grad(U);
    div(phi,omega)  Gauss linearUpwind grad(U);
    div(phi,nuTilda) Gauss upwind;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}

wallDist
{
    method meshWave;
}


// ************************************************************************* //
```

### `system/blockMeshDict`

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  v2412                                 |
|   \  /    A nd           | Website:  www.openfoam.com                      |
|    \/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
                             
                     
scale   1;

vertices
(
(0 0 -0.5) //0
(2 0 -0.5) //1
(3 0 -0.5) //2
(15 0 -0.5) //3
(15 2 -0.5) //4
(15 3 -0.5) //5
(15 5 -0.5) //6
(3 5 -0.5) //7
(2 5 -0.5) //8
(0 5 -0.5) //9
(0 3 -0.5) //10
(0 2 -0.5) //11
(2 2 -0.5) //12
(3 2 -0.5) //13
(3 3 -0.5) //14
(2 3 -0.5) //15

(0 0 0.5) //16
(2 0 0.5) //17
(3 0 0.5) //18
(15 0 0.5) //19
(15 2 0.5) //20
(15 3 0.5) //21
(15 5 0.5) //22
(3 5 0.5) //23
(2 5 0.5) //24
(0 5 0.5) //25
(0 3 0.5) //26
(0 2 0.5) //27
(2 2 0.5) //28
(3 2 0.5) //29
(3 3 0.5) //30
(2 3 0.5) //31
);

blocks
(
hex (0 1 12 11 16 17 28 27) (100 50 1) simpleGrading (1 1 1)
hex (11 12 15 10 27 28 31 26) (100 50 1) simpleGrading (1 1 1)
hex (10 15 8 9 26 31 24 25) (100 50 1) simpleGrading (1 1 1)
hex (15 14 7 8 31 30 23 24) (100 50 1) simpleGrading (1 1 1)
hex (1 2 13 12 17 18 29 28) (100 50 1) simpleGrading (1 1 1)
hex (14 5 6 7 30 21 22 23) (200 50 1) simpleGrading (4 1 1)
hex (13 4 5 14 29 20 21 30) (200 50 1) simpleGrading (4 1 1)
hex (2 3 4 13 18 19 20 29) (200 50 1) simpleGrading (4 1 1)
);

edges
(
);

boundary
(
outlet
{
type patch;
faces
(
(3 4 20 19)
(4 5 21 20)
(5 6 22 21)
);
}

inlet
{
type patch;
faces
(
(11 0 16 27)
(10 11 27 26)
(9 10 26 25)
);
}

wall1
{
type wall;
faces
(
(6 7 23 22)
(7 8 24 23)
(8 9 25 24)
);
}

wall2
{
type wall;
faces
(
(0 1 17 16)
(1 2 18 17)
(2 3 19 18)

);
}

cylinder
{
type wall;
faces
(
(15 12 28 31)
(14 15 31 30)
(12 13 29 28)
(13 14 30 29)
);
}


);

mergePatchPairs
(
);

// ************************************************************************* //
```

### `0/nuTilda`

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2412                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      nuTilda;
}

dimensions      [0 2 -1 0 0 0 0];
internalField   uniform 1e-6;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 1e-6;
    }
    outlet
    {
        type            zeroGradient;
    }
    wall1
    {
        type            fixedValue;
        value           uniform 0;
    }
    wall2
    {
        type            fixedValue;
        value           uniform 0;
    }
    defaultfaces
    {
        type            empty;
    }
    cylinder
    {
        type            fixedValue;
        value           uniform 0;
    }
}
```

### `0/p`

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  v2412                                 |
|   \  /    A nd           | Website:  www.openfoam.com                      |
|    \/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      p;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 101325;

boundaryField
{	
    wall1
    {
        type            fixedFluxPressure;
        value           $internalField;
    }
	
	wall2
    {
        type            fixedFluxPressure;
        value           $internalField;
    }
	
	cylinder
    {
        type            fixedFluxPressure;
        value           $internalField;
    }
	
    inlet
    {
        type            fixedFluxPressure;
        value           $internalField;
    }
	
    outlet
    {
        type            fixedValue;
        value           $internalField;
    }
	
    defaultFaces
    {
        type            empty;
    }
}

// ************************************************************************* //
```

### `0/U`

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  v2412                                 |
|   \  /    A nd           | Website:  www.openfoam.com                      |
|    \/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    location    "0";
    object      U;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (1 0 0);

boundaryField
{
    wall1
    {
        type            fixedValue;
        value           uniform (0 0 0);
    }
	
	wall2
    {
        type            fixedValue;
        value           uniform (0 0 0);
    }
	
	cylinder
    {
        type            fixedValue;
        value           uniform (0 0 0);
    }
	
    inlet
    {
        type            fixedValue;
        value           $internalField;
    }
	
    outlet
    {
        type            pressureInletOutletVelocity;
        value           uniform (0 0 0);
    }
	
    defaultFaces
    {
        type            empty;
    }

}

// ************************************************************************* //
```

### `0/nut`

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  v2412                                 |
|   \  /    A nd           | Website:  www.openfoam.com                      |
|    \/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      nut;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -1 0 0 0 0];

internalField   uniform 6.12e-2;

boundaryField
{
    wall1
    {
        type            nutkWallFunction;
        value           $internalField;
    }
	
	wall2
    {
        type            nutkWallFunction;
        value           $internalField;
    }
	
	cylinder
    {
        type            nutkWallFunction;
        value           $internalField;
    }
	
    inlet
    {
        type            zeroGradient;
    }
	
    outlet
    {
        type            zeroGradient;
    }
	
    defaultFaces
    {
        type            empty;
    }
}

// ************************************************************************* //
```

### `constant/turbulenceProperties`

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  v2412                                 |
|   \  /    A nd           | Website:  www.openfoam.com                      |
|    \/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      turbulenceProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

simulationType  RAS;

RAS
{
    RASModel        SpalartAllmaras;
    turbulence      on;
    printCoeffs     on;
}
// ************************************************************************* //
```

### `constant/transportProperties`

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  v2412                                 |
|   \  /    A nd           | Website:  www.openfoam.com                      |
|    \/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      transportProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

transportModel  Newtonian;

nu              2e-06;

// ************************************************************************* //
```

