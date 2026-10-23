# Double_Square_SA
| | |
|---|---|
| Solver | `pimpleFoam` |
| Turbulence | RAS SpalartAllmaras |
| Mesh cells (blockMesh) | 4200 |
| endTime / deltaT / writeInterval | 5 / 0.5 / 0.5 |
| Reference files | 12 |

## Prompt (`usr_requirement`)

> Perform an incompressible turbulent flow simulation over two square obstacle using the SpalartAllmaras turbulence model and pimpleFoam solver. The computational domain spans 0 to 5 in x direction and 0 to 2.5 in y direction and -0.5 to 0.5 in z direction. One of the square obstacle is of size  1 unit x 1 unit x 1 unit centered at 1.5 x 1.25 x 0.0 and the other square obstacle is of size 1 unit x 1 unit x 1 unit centered at 3.5 x 1.25 x 0.0. Use one cell in z direction making the geometry effectively 2D. Refine the mesh near to rectangle. Use sufficient grid points to discretize the domain and dont use more than 5000 cells in your mesh. The left boundary is the inlet which uses a uniform velocity of (1,0,0) m/s. The right boundary is the outlet, with fixed-value pressure equal to the internal field value of 101325 and a pressureInletOutletVelocity condition for velocity. Top and bottom boundaries are fixed walls with no-slip condition. The front and back faces are empty. The rectangular obstacle also has no-slip boundary condition on its surface. The kinematic viscosity is 2e-6 m2/s. Use a deltaT of 0.5 s and run till a final time of 5 s. Write the results at every 0.5 s. Use a maximum courant number of 1.0.

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

convertToMeters 1;

vertices
(
// bottom layer (z = -0.5)
    (0.0 0.0 -0.5) //  0
    (1.0 0.0 -0.5) //  1
    (2.0 0.0 -0.5) //  2
    (3.0 0.0 -0.5) //  3
    (4.0 0.0 -0.5) //  4
    (5.0 0.0 -0.5) //  5

    (0.0 0.75 -0.5) //  6
    (1.0 0.75 -0.5) //  7
    (2.0 0.75 -0.5) //  8
    (3.0 0.75 -0.5) //  9
    (4.0 0.75 -0.5) // 10
    (5.0 0.75 -0.5) // 11

    (0.0 1.75 -0.5) // 12
    (1.0 1.75 -0.5) // 13
    (2.0 1.75 -0.5) // 14
    (3.0 1.75 -0.5) // 15
    (4.0 1.75 -0.5) // 16
    (5.0 1.75 -0.5) // 17

    (0.0 2.5  -0.5) // 18
    (1.0 2.5  -0.5) // 19
    (2.0 2.5  -0.5) // 20
    (3.0 2.5  -0.5) // 21
    (4.0 2.5  -0.5) // 22
    (5.0 2.5  -0.5) // 23

// top layer (z = +0.5)
    (0.0 0.0 0.5) // 24
    (1.0 0.0 0.5) // 25
    (2.0 0.0 0.5) // 26
    (3.0 0.0 0.5) // 27
    (4.0 0.0 0.5) // 28
    (5.0 0.0 0.5) // 29

    (0.0 0.75 0.5) // 30
    (1.0 0.75 0.5) // 31
    (2.0 0.75 0.5) // 32
    (3.0 0.75 0.5) // 33
    (4.0 0.75 0.5) // 34
    (5.0 0.75 0.5) // 35

    (0.0 1.75 0.5) // 36
    (1.0 1.75 0.5) // 37
    (2.0 1.75 0.5) // 38
    (3.0 1.75 0.5) // 39
    (4.0 1.75 0.5) // 40
    (5.0 1.75 0.5) // 41

    (0.0 2.5  0.5) // 42
    (1.0 2.5  0.5) // 43
    (2.0 2.5  0.5) // 44
    (3.0 2.5  0.5) // 45
    (4.0 2.5  0.5) // 46
    (5.0 2.5  0.5) // 47
);

blocks
(
// bottom strip y ∈ [0,0.75]
    hex ( 0  1  7  6 24 25 31 30) (20 15 1) simpleGrading (1 1 1)
    hex ( 1  2  8  7 25 26 32 31) (20 15 1) simpleGrading (1 1 1)
    hex ( 2  3  9  8 26 27 33 32) (20 15 1) simpleGrading (1 1 1)
    hex ( 3  4 10  9 27 28 34 33) (20 15 1) simpleGrading (1 1 1)
    hex ( 4  5 11 10 28 29 35 34) (20 15 1) simpleGrading (1 1 1)

// middle strip y ∈ [0.75,1.75], skipping posts at ix=1 & ix=3
    hex ( 6  7 13 12 30 31 37 36) (20 20 1) simpleGrading (1 1 1)
    hex ( 8  9 15 14 32 33 39 38) (20 20 1) simpleGrading (1 1 1)
    hex (10 11 17 16 34 35 41 40) (20 20 1) simpleGrading (1 1 1)

// top strip y ∈ [1.75,2.5]
    hex (12 13 19 18 36 37 43 42) (20 15 1) simpleGrading (1 1 1)
    hex (13 14 20 19 37 38 44 43) (20 15 1) simpleGrading (1 1 1)
    hex (14 15 21 20 38 39 45 44) (20 15 1) simpleGrading (1 1 1)
    hex (15 16 22 21 39 40 46 45) (20 15 1) simpleGrading (1 1 1)
    hex (16 17 23 22 40 41 47 46) (20 15 1) simpleGrading (1 1 1)
);

edges
(
);

boundary
(
    inlet
    {
        type patch;
        faces
        (
            (0 6 30 24)
            (6 12 36 30)
            (12 18 42 36)
        );
    }
    outlet
    {
        type patch;
        faces
        (
            (5 11 35 29)
            (11 17 41 35)
            (17 23 47 41)
        );
    }
    bottomWall
    {
        type wall;
        faces
        (
            (0 1 25 24)
            (1 2 26 25)
            (2 3 27 26)
            (3 4 28 27)
            (4 5 29 28)
        );
    }
    topWall
    {
        type wall;
        faces
        (
            (18 19 43 42)
            (19 20 44 43)
            (20 21 45 44)
            (21 22 46 45)
            (22 23 47 46)
        );
    }
    posts
    {
        type wall;
        faces
        (
            // left square post at ix=1,iy=1
            (7 13 37 31)
            (8 14 38 32)
            (7 8 32 31)
            (13 14 38 37)
            // right square post at ix=3,iy=1
            (9 15 39 33)
            (10 16 40 34)
            (9 10 34 33)
            (15 16 40 39)
        );
    }
    frontAndBack
    {
        type empty;
        faces
        (
            // z = -0.5 faces (one per block, bottom-layer)
            (0 1 7 6)
            (1 2 8 7)
            (2 3 9 8)
            (3 4 10 9)
            (4 5 11 10)
            (6 7 13 12)
            (8 9 15 14)
            (10 11 17 16)
            (12 13 19 18)
            (13 14 20 19)
            (14 15 21 20)
            (15 16 22 21)
            (16 17 23 22)
            // z = +0.5 faces (top-layer)
            (24 25 31 30)
            (25 26 32 31)
            (26 27 33 32)
            (27 28 34 33)
            (28 29 35 34)
            (30 31 37 36)
            (32 33 39 38)
            (34 35 41 40)
            (36 37 43 42)
            (37 38 44 43)
            (38 39 45 44)
            (39 40 46 45)
            (40 41 47 46)
        );
    }
);

mergePatchPairs
(
);
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
    bottomWall
    {
        type            fixedValue;
        value           uniform 0;
    }
    topWall
    {
        type            fixedValue;
        value           uniform 0;
    }
    frontAndBack
    {
        type            empty;
    }
    posts
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
    bottomWall
    {
        type            fixedFluxPressure;
        value           $internalField;
    }
	
	topWall
    {
        type            fixedFluxPressure;
        value           $internalField;
    }
	
	posts
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
	
    frontAndBack
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
    bottomWall
    {
        type            fixedValue;
        value           uniform (0 0 0);
    }
	
	topWall
    {
        type            fixedValue;
        value           uniform (0 0 0);
    }
	
	posts
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
	
    frontAndBack
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
    bottomWall
    {
        type            nutkWallFunction;
        value           $internalField;
    }
	
	topWall
    {
        type            nutkWallFunction;
        value           $internalField;
    }
	
	posts
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
	
    frontAndBack
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

