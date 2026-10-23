# Cylinder_SA
| | |
|---|---|
| Solver | `pimpleFoam` |
| Turbulence | RAS SpalartAllmaras |
| Mesh cells (blockMesh) | 1800 |
| endTime / deltaT / writeInterval | 2 / 0.0025 / 0.05 |
| Reference files | 11 |

## Prompt (`usr_requirement`)

> do a offsetcylinder simulation using SpalartAllmaras turbulence model. Use PIMPLE algorithm. Boundary conditions specify a fixed velocity of 1m/s at the inlet (left),fixed-value pressure of 0 at the outlet (right) with zero-gradient velocity there, and no-slip conditions for walls, including the cylinder surface. Use timestep of 0.0025 and output every 0.05. Finaltime is 2. use a Newtonian transport model with nu value of 0.01 in transportProperties. Set nuTilda to 0.03 m^2/s in the domain and at the inlet (left), use inletOutlet with 0.03 at the outlet (right), and nuTilda = 0 (fixedValue) on the walls and the cylinder. Do not use more than 1800 cells in your mesh.

## Reference files

- `Allrun`
- `system/fvSolution`
- `system/controlDict`
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
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2412                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
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
    p
    {
        solver          GAMG;
        smoother        DIC;

        tolerance       1e-6;
        relTol          0.1;
    }

    pFinal
    {
        $p;
        relTol          0;
    }

    "U.*"
    {
        solver          PBiCGStab;
        preconditioner  DILU;

        tolerance       1e-5;
        relTol          0;
    }
   "(k|nuTilda|s)"
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-05;
        relTol          0;
    }
    kFinal
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-8;
        relTol          0;
    }
    nuTildaFinal
    {
        solver          smoothSolver;         // ✅ Solver type
        smoother        GaussSeidel;          // ✅ Smoother for stability
        tolerance       1e-8;                 // ✅ Tighter tolerance for final iteration
        relTol          0;                    // ✅ Ensure full convergence (no relative tolerance)
    }
}

PIMPLE
{
    momentumPredictor   no;
    nOuterCorrectors    5;
    nCorrectors         1;
    nNonOrthogonalCorrectors 0;
}


// ************************************************************************* //
```

### `system/controlDict`

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
    class       dictionary;
    location    "system";
    object      controlDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

application     pimpleFoam;

startFrom       startTime;

startTime       0;

stopAt          endTime;

endTime         2;

deltaT          0.0025;

writeControl    runTime;

writeInterval   0.05;

purgeWrite      0;

writeFormat     ascii;

writePrecision  6;

writeCompression off;

timeFormat      general;

timePrecision   6;

runTimeModifiable true;


// ************************************************************************* //
```

### `system/fvSchemes`

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
    default         leastSquares;
}

divSchemes
{
    default         none;

    div(phi,U)      Gauss linear;
    div(phi,k)      Gauss limitedLinear 1;
    div((nuEff*dev2(T(grad(U)))))  Gauss linear;
    div(phi,nuTilda) bounded Gauss upwind;
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
    method          meshWave;  // Added to define the wall distance calculation
}


// ************************************************************************* //
```

### `system/blockMeshDict`

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
    class       dictionary;
    object      blockMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

convertToMeters 1;

vertices
(
    (1 0 -1)
    (1.4 0 -1)
    (5 0 -1)
    (5 0.989949 -1)
    (0.989949 0.989949 -1)
    (0.707107 0.707107 -1)
    (5 2.5 -1)
    (0.989949 2.5 -1)
    (0 2.5 -1)
    (0 1.4 -1)
    (0 1 -1)
    (-1 0 -1)
    (-1.4 0 -1)
    (-5 0 -1)
    (-5 0.989949 -1)
    (-0.989949 0.989949 -1)
    (-0.707107 0.707107 -1)
    (-5 2.5 -1)
    (-0.989949 2.5 -1)
    (5 -0.989949 -1)
    (0.989949 -0.989949 -1)
    (0.707107 -0.707107 -1)
    (5 -1.5 -1)
    (0.989949 -1.5 -1)
    (0 -1.5 -1)
    (0 -1.4 -1)
    (0 -1 -1)
    (-5 -0.989949 -1)
    (-0.989949 -0.989949 -1)
    (-0.707107 -0.707107 -1)
    (-5 -1.5 -1)
    (-0.989949 -1.5 -1)
    (1 0 1)
    (1.4 0 1)
    (5 0 1)
    (5 0.989949 1)
    (0.989949 0.989949 1)
    (0.707107 0.707107 1)
    (5 2.5 1)
    (0.989949 2.5 1)
    (0 2.5 1)
    (0 1.4 1)
    (0 1 1)
    (-1 0 1)
    (-1.4 0 1)
    (-5 0 1)
    (-5 0.989949 1)
    (-0.989949 0.989949 1)
    (-0.707107 0.707107 1)
    (-5 2.5 1)
    (-0.989949 2.5 1)
    (5 -0.989949 1)
    (0.989949 -0.989949 1)
    (0.707107 -0.707107 1)
    (5 -1.5 1)
    (0.989949 -1.5 1)
    (0 -1.5 1)
    (0 -1.4 1)
    (0 -1 1)
    (-5 -0.989949 1)
    (-0.989949 -0.989949 1)
    (-0.707107 -0.707107 1)
    (-5 -1.5 1)
    (-0.989949 -1.5 1)
);

blocks
(
    hex (5 4 9 10 37 36 41 42) (10 10 1) simpleGrading (1 1 1)
    hex (0 1 4 5 32 33 36 37) (10 10 1) simpleGrading (1 1 1)
    hex (1 2 3 4 33 34 35 36) (10 10 1) simpleGrading (1 1 1)
    hex (4 3 6 7 36 35 38 39) (10 10 1) simpleGrading (1 1 1)
    hex (9 4 7 8 41 36 39 40) (10 10 1) simpleGrading (1 1 1)
    hex (15 16 10 9 47 48 42 41) (10 10 1) simpleGrading (1 1 1)
    hex (12 11 16 15 44 43 48 47) (10 10 1) simpleGrading (1 1 1)
    hex (13 12 15 14 45 44 47 46) (10 10 1) simpleGrading (1 1 1)
    hex (14 15 18 17 46 47 50 49) (10 10 1) simpleGrading (1 1 1)
    hex (15 9 8 18 47 41 40 50) (10 10 1) simpleGrading (1 1 1)
    hex (26 25 20 21 58 57 52 53) (10 10 1) simpleGrading (1 1 1)
    hex (21 20 1 0 53 52 33 32) (10 10 1) simpleGrading (1 1 1)
    hex (20 19 2 1 52 51 34 33) (10 10 1) simpleGrading (1 1 1)
    hex (23 22 19 20 55 54 51 52) (10 5 1) simpleGrading (1 1 1)
    hex (24 23 20 25 56 55 52 57) (10 5 1) simpleGrading (1 1 1)
    hex (28 29 11 12 60 61 43 44) (10 10 1) simpleGrading (1 1 1)
    hex (25 26 29 28 57 58 61 60) (10 10 1) simpleGrading (1 1 1)
    hex (27 28 12 13 59 60 44 45) (10 10 1) simpleGrading (1 1 1)
    hex (30 31 28 27 62 63 60 59) (10 5 1) simpleGrading (1 1 1)
    hex (31 24 25 28 63 56 57 60) (10 5 1) simpleGrading (1 1 1)
);

edges
(
    arc 5 0 (0.92388 0.382683 -1)
    arc 5 10 (0.382683 0.923879 -1)
    arc 1 4 (1.29343 0.535757 -1)
    arc 4 9 (0.535757 1.29343 -1)
    arc 32 37 (0.92388 0.382683 1)
    arc 37 42 (0.382683 0.923879 1)
    arc 33 36 (1.29343 0.535757 1)
    arc 36 41 (0.535757 1.29343 1)
    arc 11 16 (-0.923879 0.382683 -1)
    arc 16 10 (-0.382683 0.923879 -1)
    arc 12 15 (-1.29343 0.535757 -1)
    arc 15 9 (-0.535757 1.29343 -1)
    arc 43 48 (-0.923879 0.382683 1)
    arc 48 42 (-0.382683 0.923879 1)
    arc 44 47 (-1.29343 0.535757 1)
    arc 47 41 (-0.535757 1.29343 1)
    arc 0 21 (0.923879 -0.382683 -1)
    arc 21 26 (0.382683 -0.923879 -1)
    arc 1 20 (1.29343 -0.535757 -1)
    arc 20 25 (0.535757 -1.29343 -1)
    arc 32 53 (0.923879 -0.382683 1)
    arc 53 58 (0.382683 -0.923879 1)
    arc 33 52 (1.29343 -0.535757 1)
    arc 52 57 (0.535757 -1.29343 1)
    arc 11 29 (-0.923879 -0.382683 -1)
    arc 29 26 (-0.382683 -0.923879 -1)
    arc 12 28 (-1.29343 -0.535757 -1)
    arc 28 25 (-0.535757 -1.29343 -1)
    arc 43 61 (-0.923879 -0.382683 1)
    arc 61 58 (-0.382683 -0.923879 1)
    arc 44 60 (-1.29343 -0.535757 1)
    arc 60 57 (-0.535757 -1.29343 1)
);

defaultPatch
{
    type empty;
}

boundary
(
    left
    {
        type patch;
        faces
        (
            (17 14 46 49)
            (14 13 45 46)
            (13 27 59 45)
            (27 30 62 59)
        );
    }
    right
    {
        type patch;
        faces
        (
            (22 19 51 54)
            (19 2 34 51)
            (2 3 35 34)
            (3 6 38 35)
        );
    }
    down
    {
        type wall;
        faces
        (
            (30 31 63 62)
            (31 24 56 63)
            (24 23 55 56)
            (23 22 54 55)
        );
    }
    up
    {
        type wall;
        faces
        (
            (6 7 39 38)
            (7 8 40 39)
            (8 18 50 40)
            (18 17 49 50)
        );
    }
    cylinder
    {
        type wall;
        faces
        (
            (0 5 37 32)
            (5 10 42 37)
            (10 16 48 42)
            (16 11 43 48)
            (11 29 61 43)
            (29 26 58 61)
            (26 21 53 58)
            (21 0 32 53)
        );
    }
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
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -1 0 0 0 0];

internalField   uniform 0.03;

boundaryField
{
    left
    {
        type            fixedValue;
        value           uniform 0.03;
    }

    right
    {
        type            inletOutlet;
        inletValue      uniform 0.03;
        value           uniform 0.03;
    }

    up
    {
        type            fixedValue;
        value           uniform 0;
    }

    down
    {
        type            fixedValue;
        value           uniform 0;
    }
    
    cylinder
    {
        type            fixedValue;
        value           uniform 0;
    }
    
    defaultFaces
    {
        type            empty;
    }
}

// ************************************************************************* //
```

### `0/p`

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
    object      p;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    left
    {
        type            zeroGradient;
    }

    right
    {
        type            fixedValue;
        value           uniform 0;
    }

    down
    {
        type            zeroGradient;
    }

    up
    {
        type            zeroGradient;
    }

    cylinder
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

### `0/U`

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
    class       volVectorField;
    object      U;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{
    left
    {
        type            fixedValue;
        value           uniform (1 0 0);
    }

    right
    {
        type            zeroGradient;
    }

    down
    {
        type            noSlip;
    }

    up
    {
        type            noSlip;
    }

    cylinder
    {
        type            noSlip;
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
    object      nut;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -1 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    left
    {
        type            zeroGradient;
    }

    right
    {
        type            zeroGradient;
    }

    up
    {
        type            zeroGradient;
    }

    down
    {
        type            zeroGradient;
    }
    
    cylinder
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
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2412                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      turbulenceProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

simulationType RAS;

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
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2412                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
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

nu              0.01;

// ************************************************************************* //
```

