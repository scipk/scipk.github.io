%% HW6 - TB-18.1 and PB-14.1
% By Parham Khodadi
clear; clc; close all;

%% ==========================
%  (1) TB-18.1
%  ==========================
fprintf('============================================================\n');
fprintf('(1) TB-18.1\n');
fprintf('============================================================\n');

% Problem data
A = [1, 1; ...
     1, 1.0001; ...
     1, 1.0001];

b = [2; 0.0001; 4.0001];

% A^+ = (A^T A)^{-1} A^T
Api_exact = (A' * A)^(-1) * A';

% P = A A^+
P_exact = A*Api_exact;

% x = A^+ b
x_exact = Api_exact * b;

% y = A x
y_exact = A*x_exact;

fprintf('\nPart A:\n');
fprintf('A^+ (exact) =\n');
disp(Api_exact);
fprintf('P = A*A^+ (exact) =\n');
disp(P_exact);

fprintf('\nPart B:\n');
fprintf('x (exact) = \n');
disp(x_exact);
fprintf('y (exact) = \n');
disp(y_exact);

%% Part C/D
[U,S,V] = svd(A);
sigma = diag(S);
sigma1 = sigma(1);
sigman = sigma(2);

kappaA = sigma1 / sigman;
cos_theta = norm(y_exact,2) / norm(b,2);
theta = acos(cos_theta);
eta = norm(A,2) * norm(x_exact,2) / norm(y_exact,2);

fprintf('\nPart C:\n');
fprintf('sigma_1              = %.16e\n', sigma1);
fprintf('sigma_n              = %.16e\n', sigman);
fprintf('kappa(A)             = %.16e\n', kappaA);
fprintf('cos(theta)           = %.16e\n', cos_theta);
fprintf('theta (radians)      = %.16e\n', theta);
fprintf('theta (degrees)      = %.16f\n', theta*180/pi);
fprintf('eta                  = %.16e\n', eta);

k_b_to_y = 1 / cos_theta;
k_b_to_x = kappaA / (eta * cos_theta);
k_A_to_y = kappaA / cos_theta;
k_A_to_x = kappaA + (kappaA^2) * tan(theta) / eta;

fprintf('\nPart D:\n');
fprintf('kappa(b -> y)        = %.16e\n', k_b_to_y);
fprintf('kappa(b -> x)        = %.16e\n', k_b_to_x);
fprintf('kappa(A -> y)        = %.16e\n', k_A_to_y);
fprintf('kappa(A -> x)        = %.16e\n', k_A_to_x);

%% Part E

fprintf('\nPart E:\n')

% Set a small relative perturbation size
epsilon = 1e-8; 

% --- 1. b -> y ---
% Worst-case db must be entirely in the column space of A.
db_y = (y_exact / norm(y_exact, 2)) * epsilon * norm(b, 2);

% --- 2. b -> x ---
% Worst-case db aligns with the left singular vector for the smallest singular value.
u_n = U(:, 2); 
db_x = u_n * epsilon * norm(b, 2);

% --- 3. A -> y ---
% Worst-case dA maps the most sensitive right singular vector (v_n) to the residual space.
r = b - y_exact;
u_r = r / norm(r, 2);
v_n = V(:, 2);
dA_y = u_r * v_n' * epsilon * norm(A, 2);

% --- 4. A -> x ---
% Worst-case dA maps v_n to a specific linear combination of u_n and u_r.
w1 = -(v_n' * x_exact) / sigman;
w2 = norm(r, 2) / (sigman^2);
norm_w = sqrt(w1^2 + w2^2);

c1 = w1 / norm_w;
c2 = w2 / norm_w;

u_opt = c1 * u_n + c2 * u_r;
dA_x = u_opt * v_n' * epsilon * norm(A, 2);

fprintf('\\delta b_y = \\begin{bmatrix} %.4e \\\\ %.4e \\\\ %.4e \\end{bmatrix}\n\n', db_y(1), db_y(2), db_y(3));
fprintf('\\delta b_x = \\begin{bmatrix} %.4e \\\\ %.4e \\\\ %.4e \\end{bmatrix}\n\n', db_x(1), db_x(2), db_x(3));
fprintf('\\delta A_y = \\begin{bmatrix} %.4e & %.4e \\\\ %.4e & %.4e \\\\ %.4e & %.4e \\end{bmatrix}\n\n', dA_y(1,1), dA_y(1,2), dA_y(2,1), dA_y(2,2), dA_y(3,1), dA_y(3,2));
fprintf('\\delta A_x = \\begin{bmatrix} %.4e & %.4e \\\\ %.4e & %.4e \\\\ %.4e & %.4e \\end{bmatrix}\n', dA_x(1,1), dA_x(1,2), dA_x(2,1), dA_x(2,2), dA_x(3,1), dA_x(3,2));

%% ==========================
%  (2) PB-14.1
%  ==========================
fprintf('\n============================================================\n');
fprintf('(2) PB-14.1\n');
fprintf('============================================================\n');

x = linspace(0,1,101)';
L = 25; 
c = zeros(L+1,1);

for k = 0:L
    A_k = x.^(0:k);
    c(k+1)=cond(A_k);
end

semilogy(0:L, c, '-o', 'LineWidth', 2)
xlabel('Polynomial Degree k')
ylabel('Condition Number')
title('Condition Number of Vandermonde Matrices')
grid on
exportgraphics(gcf, 'Figures/PB_14_1.eps', 'ContentType', 'vector')