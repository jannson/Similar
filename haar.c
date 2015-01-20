#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

//gcc -std=gnu99  haar.c -o  haar

typedef double Unit;
#define	NUM_PIXELS  4
#define NUM_PIXELS_SQUARED (NUM_PIXELS * NUM_PIXELS)

static void print_arr(Unit a[])
{
    printf("\n");
    for(int i = 0; i < NUM_PIXELS_SQUARED; i++) {
        if((i % NUM_PIXELS) == 0) {
            printf(", ");
        }
        printf("%lf ", a[i]);
    }
    printf("\n");
}

static void haar2D(Unit a[])
{
  int i;
  Unit t[NUM_PIXELS >> 1];

  // scale by 1/sqrt(128) = 0.08838834764831843:
  /*
  for (i = 0; i < NUM_PIXELS_SQUARED; i++)
    a[i] *= 0.08838834764831843;
  */

  // Decompose rows:
  for (i = 0; i < NUM_PIXELS_SQUARED; i += NUM_PIXELS) {
    int h, h1;
    Unit C = 1;

    for (h = NUM_PIXELS; h > 1; h = h1) {
      int j1, j2, k;

      h1 = h >> 1;		// h = 2*h1
      C *= 0.7071;		// 1/sqrt(2)
      for (k = 0, j1 = j2 = i; k < h1; k++, j1++, j2 += 2) {
        int j21 = j2+1;

        t[k]  = (a[j2] - a[j21]) * C;
        a[j1] = (a[j2] + a[j21]);
      }
      // Write back subtraction results:
      memcpy(a+i+h1, t, h1*sizeof(a[0]));
    }
    // Fix first element of each row:
    a[i] *= C;	// C = 1/sqrt(NUM_PIXELS)
  }
  //print_arr(a);

  // scale by 1/sqrt(128) = 0.08838834764831843:
  /*
  for (i = 0; i < NUM_PIXELS_SQUARED; i++)
    a[i] *= 0.08838834764831843;
  */

  // Decompose columns:
  for (i = 0; i < NUM_PIXELS; i++) {
    Unit C = 1;
    int h, h1;

    for (h = NUM_PIXELS; h > 1; h = h1) {
      int j1, j2, k;

      h1 = h >> 1;
      C *= 0.7071;		// 1/sqrt(2) = 0.7071
      for (k = 0, j1 = j2 = i; k < h1;
	   k++, j1 += NUM_PIXELS, j2 += 2*NUM_PIXELS) {
        int j21 = j2+NUM_PIXELS;

        t[k]  = (a[j2] - a[j21]) * C;
        a[j1] = (a[j2] + a[j21]);
      }
      // Write back subtraction results:
      for (k = 0, j1 = i+h1*NUM_PIXELS; k < h1; k++, j1 += NUM_PIXELS)
        a[j1]=t[k];
    }
    // Fix first element of each column:
    a[i] *= C;
  }
}

#define X(i,j) x[(i)*N+(j)]
static void ihaar2d(double x[], int N) {
    double e[N / 2], o[N / 2];
    int i;
    for(i = 0; i < N; i++) {
        int n;
        for(n = 1; n <= N / 2; n *= 2) {
            int k;
            for(k = 0; k < n; k++) {
                e[k] = (X(i, k) + X(i, k + n)) / sqrt(2.0);
                o[k] = (X(i, k) - X(i, k + n)) / sqrt(2.0);
            }
            for(k = 0; k < n; k++) {
                X(i, 2 * k) = e[k];
                X(i, 2 * k + 1) = o[k];
            }
            print_arr(x);
        }
    }
    for(i = 0; i < N; i++) {
        int n;
        for(n = 1; n <= N / 2; n *= 2) {
            int k;
            for(k = 0; k < n; k++) {
                e[k] = (X(k, i) + X(k + n, i)) / sqrt(2.0);
                o[k] = (X(k, i) - X(k + n, i)) / sqrt(2.0);
            }
            for(k = 0; k < n; k++) {
                X(2 * k, i) = e[k];
                X(2 * k + 1, i) = o[k];
            }
        }
    }
}

int main()
{
    //Unit a[NUM_PIXELS_SQUARED] = {83.000000 53.000000 93.000000 63.000000 82.000000 71.000000 44.000000 49.000000 51.000000 33.000000 63.000000 12.000000 78.000000 98.000000 34.000000 39.000000};
    Unit a[NUM_PIXELS_SQUARED] = {83.000000, 53.000000, 93.000000, 63.000000, 82.000000, 71.000000, 44.000000, 49.000000, 51.000000, 33.000000, 63.000000, 12.000000, 78.000000, 98.000000, 34.000000, 39.000000};

    //srand(time(NULL));
    //for(int i = 0; i < NUM_PIXELS_SQUARED; i++) {
    //    a[i] = (rand() % 100);
    //}

    //print_arr(a);

    haar2D(a);
    print_arr(a);

    ihaar2d(a, 4);
    //print_arr(a);
}

