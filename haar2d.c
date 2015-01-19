/*  Forward and backwards 2D Haar wavelet transforms.  */
#include <math.h>

#define X(i,j) x[(i)*N+(j)]

void haar2d(double x[], int N) {
    double e[N / 2], o[N / 2];
    int i;
    for(i = 0; i < N; i++) {
        int n;
        for(n = N / 2; n >= 1; n /= 2) {
            int k;
            for(k = 0; k < n; k++) {
                e[k] = X(i, 2 * k);
                o[k] = X(i, 2 * k + 1);
            }
            for(k = 0; k < n; k++) {
                X(i, k) = (e[k] + o[k]) / sqrt(2.0);
                X(i, k + n) = (e[k] - o[k]) / sqrt(2.0);
            }
        }
    }
    for(i = 0; i < N; i++) {
        int n;
        for(n = N / 2; n >= 1; n /= 2) {
            int k;
            for(k = 0; k < n; k++) {
                e[k] = X(2 * k, i);
                o[k] = X(2 * k + 1, i);
            }
            for(k = 0; k < n; k++) {
                X(k, i) = (e[k] + o[k]) / sqrt(2.0);
                X(k + n, i) = (e[k] - o[k]) / sqrt(2.0);
            }
        }
    }
}

void ihaar2d(double x[], int N) {
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
