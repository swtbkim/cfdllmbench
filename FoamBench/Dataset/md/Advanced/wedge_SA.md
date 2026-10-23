# wedge_SA
| | |
|---|---|
| Solver | `rhoCentralFoam` |
| Turbulence | RAS SpalartAllmaras |
| Mesh cells (blockMesh) | 4800 |
| endTime / deltaT / writeInterval | 0.2 / 0.0001 / 0.02 |
| Reference files | 13 |

## Prompt (`usr_requirement`)

> Perform a 2D supersonic flow simulation over a wedge. Create a 3D geometry spanning from -0.15242 m to 0.3048 m in the x-direction, 0 m to 0.1524 m in the y-direction, and -0.005 m to 0.005 m in the z-direction. The simulation starts at 0.0 seconds and runs until 0.2 seconds with a time step (deltaT) of 0.0001 seconds. The results are written every 0.02 seconds. The inlet velocity is 5 m/s, inlet temperature is 1 K and inlet pressure is 1 Pa. Use normalized thermodynamic properties where molWeight is set to 11640.3, Cp is 2.5, Pr is 1.0, and dynamic viscosity mu is 0.01. Use rhoCentralFoam solver. Use SpalartAllmaras turbulence model. The wedge surface is a slip boundary. Do not use more than 4800 cells in your mesh.

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
- `0/T`
- `0/alphat`
- `constant/turbulenceProperties`
- `constant/thermophysicalProperties`

### `Allrun`

```sh
#!/bin/sh
cd ${0%/*} || exit 1    # Run from this directory

# Source tutorial run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

application="$(getApplication)"
echo $application

runApplication blockMesh
runApplication rhoCentralFoam

#------------------------------------------------------------------------------
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
    "(rho|rhoU|rhoE)"
    {
        solver          diagonal;
    }

    "(U|e).*"
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        nSweeps         2;
        tolerance       1e-09;
        relTol          0.01;
    }

    e
    {
        $U;
        tolerance       1e-10;
        relTol          0;
    }
    nuTilda
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-7;
        relTol          0.1;
    }
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

application     rhoCentralFoam;

startFrom       startTime;

startTime       0;

stopAt          endTime;

endTime         0.2;

deltaT          0.0001;

writeControl    runTime;

writeInterval   0.02;

purgeWrite      0;

writeFormat     ascii;

writePrecision  6;

writeCompression off;

timeFormat      general;

timePrecision   6;

runTimeModifiable true;

adjustTimeStep  no;

maxCo           1;

maxDeltaT       1e-06;


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

fluxScheme      Kurganov;

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
    div(tauMC)      Gauss linear;
    div(phi,nuTilda) bounded Gauss upwind;
    div(phi,U)      bounded Gauss upwind;
}

laplacianSchemes
{
    default         Gauss linear corrected;
    laplacian(nuEff,U) Gauss linear corrected;
    laplacian(1,nuTilda) Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
    reconstruct(rho) vanLeer;
    reconstruct(U)  vanLeerV;
    reconstruct(T)  vanLeer;
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

convertToMeters 1;

vertices
(
    (-0.15242 0       -0.005)
    ( 0       0       -0.005)
    ( 0.3048  0.081670913853  -0.005)
    (-0.15242 0.1524 -0.005)
    ( 0       0.1524 -0.005)
    ( 0.3048  0.1524 -0.005)

    (-0.15242 0        0.005)
    ( 0       0        0.005)
    ( 0.3048  0.081670913853 0.005)
    (-0.15242 0.1524  0.005)
    ( 0       0.1524  0.005)
    ( 0.3048  0.1524  0.005)

);

blocks
(
    hex (0 1 4 3 6 7 10 9 ) (40 40 1) simpleGrading (1 1 1)
    hex (1 2 5 4 7 8 11 10) (80 40 1) simpleGrading (1 1 1)
);

defaultPatch
{
    type empty;
}

boundary
(
    inlet
    {
        type patch;
        faces
        (
            (0 6 9 3)
        );
    }
    outlet
    {
        type patch;
        faces
        (
            (2 5 11 8)
        );
    }
    bottom
    {
        type symmetryPlane;
        faces
        (
            (0 1 7 6)
        );
    }
    top
    {
        type symmetryPlane;
        faces
        (
            (3 9 10 4)
            (4 10 11 5)
        );
    }
    obstacle
    {
        type patch;
        faces
        (
            (1 2 8 7)
        );
    }
);


// ************************************************************************* //
```

### `0/nuTilda`

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
    object      nuTilda;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -1 0 0 0 0];

internalField   uniform 1e-5;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 1e-5;
    }

    outlet
    {
        type            fixedValue;
        value           uniform 1e-5;
    }

    bottom
    {
        type            symmetryPlane;
    }

    top
    {
        type            symmetryPlane;
    }

    obstacle
    {
        type            fixedValue;
        value           uniform 0;    // No-slip condition at walls
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

dimensions      [1 -1 -2 0 0 0 0];

internalField   uniform 1;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 1;
    }

    outlet
    {
        type            zeroGradient;
    }

    bottom
    {
        type            symmetryPlane;
    }

    top
    {
        type            symmetryPlane;
    }

    obstacle
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
    object      U;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (5 0 0);

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (5 0 0);
    }

    outlet
    {
        type            zeroGradient;
    }

    bottom
    {
        type            symmetryPlane;
    }

    top
    {
        type            symmetryPlane;
    }

    obstacle
    {
        type            slip;
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

internalField   uniform 0;

boundaryField
{
    inlet
    {
        type            calculated;
        value           uniform 0;
    }

    outlet
    {
        type            calculated;
        value           uniform 0;
    }

    bottom
    {
        type            symmetryPlane;   // Correct boundary condition
    }

    top
    {
        type            symmetryPlane;   // Correct boundary condition
    }

    obstacle
    {
        type            calculated;    // ✅ Replaced nutkWallFunction with calculated
        value           uniform 0;     // Placeholder (required even if not used)
    }

    defaultFaces
    {
        type            empty;
    }
}

// ************************************************************************* //
```

### `0/T`

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
    object      T;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 0 1 0 0 0];

internalField   uniform 1;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 1;
    }

    outlet
    {
        type            zeroGradient;
    }

    bottom
    {
        type            symmetryPlane;
    }

    top
    {
        type            symmetryPlane;
    }

    obstacle
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

### `0/alphat`

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
    object      alphat;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [1 -1 -1 0 0 0 0];

internalField   uniform 1e-5;

boundaryField
{
    inlet
    {
        type            calculated;
        value           uniform 0;
    }

    outlet
    {
        type            calculated;
        value           uniform 0;
    }

    bottom
    {
        type            symmetryPlane;
    }

    top
    {
        type            symmetryPlane;
    }

    obstacle
    {
        type            calculated;     // ✅ Replaced alphatWallFunction with calculated
        value           uniform 0;      // Placeholder required even if not directly used
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

simulationType RAS;

RAS
{
    RASModel        SpalartAllmaras;
    turbulence      on;
    printCoeffs     on;
}



// ************************************************************************* //
```

### `constant/thermophysicalProperties`

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
    object      thermophysicalProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

thermoType
{
    type            hePsiThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState perfectGas;
    specie          specie;
    energy          sensibleInternalEnergy;
}

mixture
{
    // normalised gas
    specie
    {
        molWeight       11640.3;
    }
    thermodynamics
    {
        Cp              2.5;
        Hf              0;
    }
    transport
    {
        mu              0.01;
        Pr              1;
    }
}


// ************************************************************************* //
```

